from client.publicRequests import PublicRequests
import config
from client.utils.myprogressbar import ProgressBar
import time
from pymongo import MongoClient
from urllib.parse import quote_plus

def get_last_missing_rates(product, collection_name, granularity=60):
    """Get last missing rates for a given granularity.

    Arguments :
    granularity -- period in seconds
    """
    pb = ProgressBar('Getting historic rates to database')
    pr = PublicRequests(product = product)

    mongo_uri = 'mongodb://{}:{}@{}/cryptobase'.format(
        quote_plus(credentials['USERNAME']),
        quote_plus(credentials['DATABASE_PASSWORD']),
        credentials['DATABASE_URI']
    )
    client = MongoClient(mongo_uri)
    db = client['cryptobase'] # the database
    collection = db[collection_name] # the collection

    #last_candle = collection.find({'length': granularity}).sort([('timestamp', -1)]).limit(1)[0]

    candles_timestamps = collection.distinct('timestamp')
    candles_timestamps.sort()


    start = candles_timestamps[-1] + granularity
    end = int(pr.get_time()['epoch'])
    print(pr.get_time()['iso'])
    inter_start = start
    inter_end = start + 180 * granularity

    while inter_end < end + 180 * granularity:
        pb.show_progress((inter_start - start) / (end - start))
        time.sleep(1)
        chandelier = pr.get_historic_rates(
            pr.epoch_to_iso(inter_start),
            pr.epoch_to_iso(inter_end),
            granularity)
        inter_start = inter_end
        inter_end = inter_start + 180 * granularity
        candles_to_add = []
        for row in chandelier:
            candle = {
                'timestamp': int(row[0]),
                'date': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(int(row[0]))),
                'length': granularity,
                'low_price': float(row[1]),
                'high_price': float(row[2]),
                'opening_price': float(row[3]),
                'closing_price': float(row[4]),
                'volume': float(row[5])
            }
            candle_end_time = candle['timestamp'] + granularity + 200 # +200s to be sure gdax has closed it already
            if candle_end_time < end and candle['timestamp'] not in candles_timestamps:
                candles_to_add.append(candle)
        if candles_to_add:
            print('Inserting candles.. This can be a bit long...')
            collection.insert_many(candles_to_add)
    pb.finish()

def main(product, collection, length, credentials):
    
    get_last_missing_rates(product, collection, granularity=length)


if __name__ == '__main__':
    import argparse
    import textwrap
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Complete a collection by adding the last missing candles.",
        epilog=textwrap.dedent('''

            example :
            python complete_database.py BTC-EUR btc_eur_candles_900 900
            ___
            '''))
    
    parser.add_argument("product", help="product of the collection (ex: BTC-EUR)", type=str)
    parser.add_argument("collection", help="collection to work on in the database", type=str)
    parser.add_argument("length", help="length of the candles of the given collection", type=int)
    parser.add_argument('--mode', dest='mode', type=str, default='dev', help='dev (default) or prod')

    args = parser.parse_args()

    if args.mode == 'prod':
        credentials = config.prod
    else:
        credentials = config.dev
    

    main(args.product, args.collection, args.length, credentials)