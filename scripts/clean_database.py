import pymongo
from pymongo import MongoClient
import time
import numpy as np
from client.utils.myprogressbar import ProgressBar
from urllib.parse import quote_plus
import config


def complete_raw_data(collection_name, credentials): # Not optimized
    pb = ProgressBar('Complete raw data')

    mongo_uri = 'mongodb://{}:{}@{}/cryptobase'.format(
        quote_plus(credentials['USERNAME']),
        quote_plus(credentials['DATABASE_PASSWORD']),
        credentials['DATABASE_URI']
    )
    client = MongoClient(mongo_uri)
    db = client['cryptobase']  # the database
    collection = db[collection_name]  # the collection

    cursor = collection.find({'macd': {'$exists': False}}).sort('timestamp', pymongo.ASCENDING)
    number_to_complete = cursor.count()
    print(f'{number_to_complete} candles to complete')
    completed_candles = 0
    for candle in cursor:
        pb.show_progress(completed_candles / number_to_complete)
        last_candles_timestamp = [candle['timestamp'] - (k * candle['length']) for k in range(1,26)]
        last_candles = collection.find({'timestamp': {'$in': last_candles_timestamp}})
        if last_candles.count() == 25:
            last_candles.sort('timestamp', pymongo.ASCENDING)
            last26 = []
            for last_candle in last_candles:
                last26.append(last_candle['closing_price'])
                if 'stochastic' in last_candle:
                    last_stochastic = last_candle['stochastic']
            last26.append(candle['closing_price'])
            last20 = last26[-20:]
            last12 = last26[-12:]
            bdb_low, bdb_high = bdb(last20)
            candle['bdb_low'] = bdb_low
            candle['bdb_high'] = bdb_high
            candle['mme12'] = mme12(last12)
            candle['mme26'] = mme26(last26)
            candle['macd'] = candle['mme12'] - candle['mme26']
            if candle['low_price'] != candle['high_price']:
                candle['stochastic'] = pk(candle['closing_price'], candle['low_price'], candle['high_price'])
            else:
                candle['stochastic'] = last_stochastic

            collection.replace_one({'_id': candle['_id']}, candle)
            completed_candles += 1
        else:
            print('Data missing for {} timestamp.'.format(candle['timestamp']))
    pb.finish()
    print(f'{completed_candles} candles completed')
    print(f'{number_to_complete - completed_candles} candles NOT completed')


def complete_database_with_missing_candles(collection_name, granularity, credentials):
    "Complete database with empty candles when one is missing"
    print('Complete database with missing candles')

    mongo_uri = 'mongodb://{}:{}@{}/cryptobase'.format(
        quote_plus(credentials['USERNAME']),
        quote_plus(credentials['DATABASE_PASSWORD']),
        credentials['DATABASE_URI']
    )
    client = MongoClient(mongo_uri)
    db = client['cryptobase']  # the database
    collection = db[collection_name]  # the collection

    timestamps = collection.distinct('timestamp')
    timestamps.sort()

    missing_timestamps = []

    for i in range(len(timestamps) - 1):
        current_timestamp = timestamps[i]
        while current_timestamp + granularity < timestamps[i+1]:
            missing_timestamps.append(current_timestamp + granularity)
            current_timestamp += granularity

    total_elements = len(timestamps)
    print(f'The collection {collection_name} contains {total_elements} candles.')
    print(f'{len(missing_timestamps)} candles are missing.')

    candles_to_insert = []
    for timestamp in missing_timestamps:
        
        candle = collection.find_one({'timestamp': timestamp - granularity})
        if not candle:
            candle = find_candle_in_list(timestamp - granularity, candles_to_insert)
            
        if not candle:
            raise Exception
        print(candle)
        new_candle = {
            'timestamp': candle['timestamp'] + candle['length'],
            'date': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(candle['timestamp'] + candle['length'])),
            'length': candle['length'],
            'low_price': candle['closing_price'],
            'high_price': candle['closing_price'],
            'opening_price': candle['closing_price'],
            'closing_price': candle['closing_price'],
            'volume': 0
        }

        if 'stochastic' in candle:
            new_candle['stochastic'] = candle['stochastic']
        
        candles_to_insert.append(new_candle)
 
    if len(candles_to_insert) > 0:
        print('Inserting all missing candles...')
        collection.insert_many(candles_to_insert)


def find_candle_in_list(timestamp, candles):
    result_candles = [c for c in candles if c['timestamp'] == timestamp]
    if result_candles:
        return result_candles[0]
    else:
        return {}


def remove_doublons_in_database(collection_name, credentials):
    "Remove doublons in database"
    pb = ProgressBar('Remove doublons in database')

    mongo_uri = 'mongodb://{}:{}@{}/cryptobase'.format(
        quote_plus(credentials['USERNAME']),
        quote_plus(credentials['DATABASE_PASSWORD']),
        credentials['DATABASE_URI']
    )
    client = MongoClient(mongo_uri)
    db = client['cryptobase']  # the database
    collection = db[collection_name]  # the collection

    cursor = collection.find({}, {'timestamp': 1, '_id': 0}).sort('timestamp', pymongo.DESCENDING)
    total_elements = cursor.count()
    print('The collection {} contains {} candles.'.format(collection_name, total_elements))
    print('candles to remove :')
    for i in range(total_elements - 1):
        pb.show_progress(i / total_elements)
        candle = cursor[i]
        if candle['timestamp'] == cursor[i + 1]['timestamp']:
            print(candle['timestamp'])
            collection.delete_one({'timestamp': candle['timestamp']})
    pb.finish()


def mme12(last12):
    k = 0
    result = 0
    for x in reversed(last12):
        result += float(x) * (1 - 0.154) ** k
        k += 1
    return result * 0.154


def mme26(last26):
    k = 0
    result = 0
    for x in reversed(last26):
        result += float(x) * (1 - 0.074) ** k
        k += 1
    return result * 0.074


def bdb(last20):
    last20 = [float(i) for i in last20]
    mean = np.mean(last20)
    sigma = np.std(last20, 0)
    return [mean - sigma, mean + sigma]


def pk(out, low, high):
    out = float(out)
    low = float(low)
    high = float(high)
    if high != low:
        return (out - low) / (high - low)
    else:
        return 0


def main(collection, length, credentials):
    complete_database_with_missing_candles(collection, length, credentials)
    # Remove doublons is not necessary anymore.
    #remove_doublons_in_database(collection, credentials)
    complete_raw_data(collection, credentials)


if __name__ == '__main__':
    import argparse
    import textwrap
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Clean the database by adding, removing and completing candles.",
        epilog=textwrap.dedent('''

            example :
            python clean_database.py btc_eur_candles_900 900
            ___
            '''))

    parser.add_argument("collection", help="collection to work on in the database", type=str)
    parser.add_argument("length", help="length of the candles of the given collection", type=int)
    parser.add_argument('--mode', dest='mode', type=str, default='dev', help='dev (default) or prod')
    args = parser.parse_args()

    if args.mode == 'prod':
        credentials = config.prod
    else:
        credentials = config.dev
    

    main(args.collection, args.length, credentials)
