from pymongo import MongoClient
import time
import customlog
import datetime

logger = customlog.custom_logger('client')
db = MongoClient('localhost', 27017).Cryptobase

class Ticker():
    def __init__(self, ticker):
        try:
            self.__check_ticker_keys(ticker)

            self.product = str(ticker['product'])
            self.sequence = int(ticker['sequence'])
            self.price = float(ticker['price'])
            self.open_24h = float(ticker['open_24h'])
            self.volume_24h = float(ticker['volume_24h'])
            self.low_24h = float(ticker['low_24h'])
            self.high_24h = float(ticker['high_24h'])
            self.volume_30d = float(ticker['volume_30d'])
            self.best_bid = float(ticker['best_bid'])
            self.best_ask = float(ticker['best_ask'])
            self.side = str(ticker['side'])
            self.time = datetime.datetime(ticker['time'])
            self.trade_id = int(ticker['trade_id'])
            self.last_size = float(ticker['last_size'])
        except KeyError as e:
            logger.error(f'ticker cannot be created : {e}.')
        except Exception as e:
            logger.error(f'Ticker.__init__() failed : {e}.')

    def __check_ticker_keys(self, ticker):
        required_keys = [
            "sequence",
            "price",
            "open_24h",
            "volume_24h",
            "low_24h",
            "high_24h",
            "volume_30d",
            "best_bid",
            "best_ask",
            "side",
            "time",
            "trade_id",
            "last_size"
        ]
        for key in required_keys:
            if key not in ticker:
                raise KeyError

    def save_one(self, ticker):
        tickers = db[f'tickers_{self.product}']  # the collection
        ticker = {
            "sequence": self.sequence,
            "price": self.price,
            "open_24h": self.open_24h,
            "volume_24h": self.volume_24h,
            "low_24h": self.low_24h,
            "high_24h": self.high_24h,
            "volume_30d": self.volume_30d,
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "side": self.side,
            "time": self.time,
            "trade_id":self.trade_id,
            "last_size": self.last_size
        }
        tickers.insert_one(ticker)


class Decision():
    def __init__(self, product='BTC-EUR'):
        self.product = product

    def save_one(self, decision):
        decisions = db[f'decisions_{self.product}']
        decisions.insert_one(decision)

    def get_last(self):
        decisions = db[f'decisions_{self.product}']
        return decisions.find().sort({'timestamp': -1}).limit(1)[0] #find latest


class Candles():
    def __init__(self, product):
        self.product = product

    def get_last_candles(self, granularity, candles_number):
        current_time = time.gmtime()
        candles = []
        for i in range(candles_number):
            start = current_time - ((i+1) * granularity)
            end = current_time - (i * granularity)
            candle = self.__aggregate_into_candle(start, end)
            candles.append(candle)
        return candles

    def __aggregate_into_candle(self, start, end):
        tickers = db[f'tickers_{self.product}']  # the collection

        pipeline = [
            {"$match": {
                "timestamp": {"$gte": start, "$lt": end}
                }
            },
            {"$sort": {"timestamp": 1}},
            {"$group": {
                "_id": 0,
                "volume": {"$sum": "$volume"},
                "min":{"$min": "$price"},
                "max":{"$max": "$price"},
                "open":{"$first": "$price"},
                "close":{"$last": "$price"},
                }
            },
        ]

        return tickers.aggregate(pipeline)


