import urllib.request as req
import json as js
import os
import csv
import time
from pymongo import MongoClient
from client.utils.myprogressbar import ProgressBar


class PublicRequests():
    def __init__(self, url='https://api.gdax.com', product='LTC-EUR'):
        self.url = url
        self.product = product

    def __public_request(self, method):
        urlpath = self.url + '/' + method
        try:
            res = req.urlopen(urlpath)
            if res.status == 200:
                data = js.loads(res.read().decode('utf-8'))
                return data
            else:
                print('Status : {}, {}'.format(res.status, res.getheaders()))
                return {"status": res.status, "headers": res.getheaders()}
        except req.HTTPError as e:
            print('Error on public_request:')
            print('> URL : {}'.format(e.url))
            print('> Status : {}'.format(e.code))
            print('> Reason : {}'.format(e.reason))
            print('> Headers : {}'.format(e.headers))
            raise

    def get_time(self):
        """Get time in ISO and since EPOCH."""
        return self.__public_request('time')

    def get_products(self):
        """Get the available products."""
        return self.__public_request('products')

    def get_currencies(self):
        """Get the available currencies."""
        return self.__public_request('currencies')

    def get_product_order_book(self, level=1):
        """Get the product order book."""
        method = 'products/' + self.product + '/book?level=' + str(level)
        return self.__public_request(method)

    def get_product_ticker(self):
        """Get the product ticker.
        You should consider using websocket instead.
        """
        method = 'products/' + self.product + '/ticker'
        return self.__public_request(method)

    def get_product_trades(self, before='', after='', limit=100):
        """Get product trades.
        This request is paginated.
        """
        if before != '' or after != '' or limit != 100:
            params = '?'
            if before != '':
                params += 'before=' + str(before) + '&'
            if after != '':
                params += 'after=' + str(after) + '&'
            if limit != 100:
                params += 'limit=' + str(limit)

        method = 'products/' + self.product + '/trades' + params
        return self.__public_request(method)

    def get_historic_rates(self, start, end, granularity):
        """Get historic rates.

        Arguments:
        start -- date (iso)
        end -- date (iso)
        granularity -- duration (seconds)

        Result:
        [time, low, high, open, close, volume]
        time: since EPOCH
        """
        params = ('?start=' + str(start) + '&end=' + str(end) +
                  '&granularity=' + str(granularity))
        method = 'products/' + self.product + '/candles' + params
        return self.__public_request(method)

    def get_historic_rates_data_long(self, start=1496275200,
                                     end=1496707200, granularity=60,
                                     path='/Users/Antoine/Desktop/GDAXPY'):
        """Get historic rates on a longer period.

        Arguments :
        start -- seconds since epoch
        end -- seconds since epoch
        default = 01/06/2017 & 06/06/2017
        granularity -- period in seconds
        """
        pb = ProgressBar('Getting historic rates')
        os.chdir(path)
        inter_start = start
        inter_end = start + 180 * granularity  # s'occuper des conversions
        file = ('historic_rates(' + self.product + ')(' +
                self.epoch_to_iso(start) + ' - ' +
                self.epoch_to_iso(end) + ')-' + str(granularity) + '.csv')
        with open(file, 'w', newline='') as f:
            writer = csv.writer(f)
            while inter_end < end:
                pb.show_progress((inter_start - start) / (end - start))
                time.sleep(1)
                chandelier = self.get_historic_rates(
                    self.epoch_to_iso(inter_start),
                    self.epoch_to_iso(inter_end),
                    granularity)
                chandelier.reverse()
                inter_start = inter_end
                inter_end = inter_start + 180 * granularity
                for candle in chandelier:
                    writer.writerow(candle)
        pb.finish()
        return file

    def get_last_missing_rates(self, collection_name, granularity=60):
        """Get last missing rates for a given granularity.

        Arguments :
        granularity -- period in seconds
        """
        pb = ProgressBar('Getting historic rates to database')

        client = MongoClient('localhost', 27017)
        db = client['Cryptobase'] # the database
        collection = db[collection_name] # the collection

        last_candle = collection.find({'length': granularity}).sort([('timestamp', -1)]).limit(1)[0]
        start = last_candle['timestamp'] + granularity
        end = int(self.get_time()['epoch'])
        print(self.get_time()['iso'])
        inter_start = start
        inter_end = start + 180 * granularity

        while inter_end < end + 180 * granularity:
            pb.show_progress((inter_start - start) / (end - start))
            time.sleep(1)
            chandelier = self.get_historic_rates(
                self.epoch_to_iso(inter_start),
                self.epoch_to_iso(inter_end),
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
                if candle_end_time < end and collection.count({'timestamp': candle['timestamp']}) == 0:
                    candles_to_add.append(candle)
            if candles_to_add:
                collection.insert_many(candles_to_add)
        pb.finish()


    def epoch_to_iso(self, epoch_time):
        t = time.gmtime(epoch_time)
        iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', t)
        return iso
