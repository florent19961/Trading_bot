from pymongo import MongoClient, IndexModel
from pymodm import MongoModel, EmbeddedMongoModel, fields, connect
from pymodm.queryset import QuerySet
from pymodm.manager import Manager
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import config
import logging
import os

user_name = os.environ.get('USERNAME')
db_password = os.environ.get('DATABASE_PASSWORD')
db_uri = os.environ.get('DATABASE_URI')

logger = logging.getLogger('client')

db = MongoClient('localhost', 27017).Cryptobase
mongo_uri = 'mongodb://{}:{}@{}/cryptobase'.format(
    quote_plus(user_name), quote_plus(db_password), db_uri)
connect(mongo_uri)

products_list = ('BTC-EUR', 'ETH-EUR', 'LTC-EUR', 'BCH-EUR')


# Trades
class TickerData(EmbeddedMongoModel):
    sequence = fields.IntegerField(min_value=0)
    open_24h = fields.FloatField(min_value=0)
    volume_24h = fields.FloatField(min_value=0)
    low_24h = fields.FloatField(min_value=0)
    high_24h = fields.FloatField(min_value=0)
    volume_30d = fields.FloatField(min_value=0)
    best_bid = fields.FloatField(min_value=0)
    best_ask = fields.FloatField(min_value=0)


class Trade(MongoModel):
    trade_id = fields.IntegerField(min_value=0)
    time = fields.DateTimeField(required=True)
    product_id = fields.CharField(required=True, choices=products_list)
    size = fields.FloatField(required=True)
    price = fields.FloatField(required=True)
    side = fields.CharField(required=True, choices=('buy', 'sell'))
    ticker_data = fields.EmbeddedDocumentField(TickerData, required=False)

    class Meta:
        final = True
        indexes = [
            IndexModel([('product_id', 1), ('time', -1)])
        ]


# Decisions
class OrderBook(EmbeddedMongoModel):
    sequence = fields.IntegerField(min_value=0)
    bids = fields.ListField()
    asks = fields.ListField()


class DecisionManager(Manager):
    def last_decision(self, product_id):
        '''Return last decision.'''
        return self.raw({'product_id': product_id}).order_by([('time', -1)]).limit(1)[0].decision


class Decision(MongoModel):
    time = fields.DateTimeField(required=True)
    product_id = fields.CharField(required=True, choices=products_list)
    decision = fields.CharField(required=True, choices=('Buy', 'Sell', 'Wait'))
    strategy = fields.CharField(required=True)
    order_book = fields.EmbeddedDocumentField(OrderBook, required=False)

    objects = DecisionManager()
    class Meta:
        final = True
        indexes=[IndexModel([('product_id', 1), ('time', -1)])]


# Candles
class AggregatedData(EmbeddedMongoModel):
    mme12 = fields.FloatField(min_value=0)
    mme26 = fields.FloatField(min_value=0)
    macd = fields.FloatField()
    lower_bollinger = fields.FloatField(min_value=0)
    upper_bollinger = fields.FloatField(min_value=0)


class Candle(MongoModel):
    time = fields.DateTimeField(required=True)
    product_id = fields.CharField(required=True, choices=products_list)
    length = fields.IntegerField(min_value=60, required=True)
    low = fields.FloatField(min_value=0, required=True)
    high = fields.FloatField(min_value=0, required=True)
    open = fields.FloatField(min_value=0, required=True)
    close = fields.FloatField(min_value=0, required=True)
    volume = fields.FloatField(min_value=0, required=True)
    aggregated_data = fields.EmbeddedDocumentField(AggregatedData, required=False)

    class Meta:
        final = True
        indexes=[IndexModel([('product_id', 1), ('length', 1), ('time', -1)])]


class CandlesFromTrades():
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


