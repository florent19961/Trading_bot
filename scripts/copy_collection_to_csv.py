import csv
import pymongo
from pymongo import MongoClient
import config
from urllib.parse import quote_plus


def copy_db_csv(collection_name,file_name,credentials,path):
    mongo_uri = 'mongodb://{}:{}@{}/cryptobase'.format(
        quote_plus(credentials['USERNAME']),
        quote_plus(credentials['DATABASE_PASSWORD']),
        credentials['DATABASE_URI']
    )
    client = MongoClient(mongo_uri)
    db = client['cryptobase'] # the database
    collection = db[collection_name] # the collection

    first_row = [
        "timestamp",
        "date",
        "length",
        "low_price" ,
        "high_price",
        "opening_price",
        "closing_price",
        "volume" ,
        "bdb_low",
        "bdb_high",
        "mme12",
        "mme26",
        "stochastic",
        "macd"
    ]
    with open(path + '/' + file_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(first_row)
        for candle in collection.find({'macd': {'$exists': True}}).sort('timestamp', pymongo.ASCENDING):
            new_row = [
                candle['timestamp'],
                candle['date'],
                candle['length'],
                candle['low_price'],
                candle['high_price'],
                candle['opening_price'],
                candle['closing_price'],
                candle['volume'],
                candle['bdb_low'],
                candle['bdb_high'],
                candle['mme12'],
                candle['mme26'],
                candle['stochastic'],
                candle['macd']
            ]
            writer.writerow(new_row)


if __name__ == '__main__':
    import argparse
    import textwrap
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Export a collection to CSV file.",
        epilog=textwrap.dedent('''

            example :
            python copy_collection_to_csv.py btc_eur_candles_900 btc_eur_900.csv
            ___
            '''))
        
    parser.add_argument("collection", help="collection to work on in the database", type=str)
    parser.add_argument("file_name", help="name of the csv file (example.csv)", type=str)
    parser.add_argument('--path', dest='path', type=str, default='../data',
                        help='Change the path to save the csv file (default: ../data)')
    parser.add_argument('--mode', dest='mode', type=str, default='dev', help='dev (default) or prod')
    args = parser.parse_args()

    if args.mode == 'prod':
        credentials = config.prod
    else:
        credentials = config.dev
    


    copy_db_csv(args.collection, args.file_name, credentials, path=args.path)