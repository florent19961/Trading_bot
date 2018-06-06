from pymongo import MongoClient
import time
from datetime import datetime, timedelta
import logging


logger = logging.getLogger('client')
db = MongoClient('localhost', 27017).Cryptobase

class Ticker():
    def __init__(self, ticker):
        try:
            self.__check_ticker_keys(ticker)

            self.product = str(ticker['product_id'])
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
            self.time = datetime.strptime(ticker['time'],'%Y-%m-%dT%H:%M:%S.%fZ')
            self.trade_id = int(ticker['trade_id'])
            self.last_size = float(ticker['last_size'])
        except KeyError as e:
            logger.error(f'ticker cannot be created : {e}')
        except Exception as e:
            logger.error(f'Ticker.__init__() failed : {e}')

    def __check_ticker_keys(self, ticker):
        required_keys = [
            "product_id",
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
                logger.error(f'missing \"{key}\" key in ticker')
                raise KeyError

    def save_one(self):
        try:
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
        except Exception as e:
            logger.error(f'Ticker could not be saved : {e}')


class Decisions():
    def __init__(self, product='BTC-EUR'):
        self.product = product

    def save_one(self, decision, strategy, price):
        try:
            decisions = db[f'decisions_{self.product}']
            decision_to_save = {
                'time': datetime.utcnow(),
                'decision': decision,
                'strategy': strategy,
                'price': price
            }
            decisions.insert_one(decision_to_save)
        except Exception as e:
            logger.error(f'Ticker could not be saved : {e}')

    def get_last(self):
        try:
            decisions = db[f'decisions_{self.product}']
            return decisions.find().sort({'time': -1}).limit(1)[0]['decision'] #find latest
        except:
            return 'Wait'


class Candles():
    def __init__(self, product):
        self.product = product

    def get_last_candles(self, granularity, candles_number):
        current_time = datetime.utcnow()
        candles = []
        for i in range(candles_number):
            start = current_time - timedelta(seconds=(i+1) * granularity)
            end = current_time - timedelta(seconds=i * granularity)
            candle = self.__aggregate_into_candle(start, end)
            candles.append(candle)
        return candles

    def get_last_candles_price_list(self, granularity, candles_number):
        candles = self.get_last_candles(granularity, candles_number)
        price_list = []
        for candle in candles:
            price_list.append(candle['close'])
        return price_list

    def __aggregate_into_candle(self, start, end):
        tickers = db[f'tickers_{self.product}']  # the collection

        pipeline = [
            {"$match": {
                "time": {"$gte": start, "$lt": end}
                }
            },
            {"$sort": {"timestamp": 1}},
            {"$group": {
                "_id": 0,
                "volume": {"$sum": "$last_size"},
                "min":{"$min": "$price"},
                "max":{"$max": "$price"},
                "open":{"$first": "$price"},
                "close":{"$last": "$price"},
                }
            },
        ]

        aggregated_candle = list(tickers.aggregate(pipeline))
        if len(aggregated_candle) > 0:
            candle = aggregated_candle[0]
        else:
            candle = {
                "_id": 0,
                "volume": 0,
                "min":0,
                "max":0,
                "open":0,
                "close":0,
            }

        return candle


