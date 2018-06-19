import urllib.request as req
import json as js
import os
import csv
import time
from pymongo import MongoClient
from client.utils.myprogressbar import ProgressBar
from datetime import datetime

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


    def epoch_to_iso(self, epoch_time):
        t = time.gmtime(epoch_time)
        iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', t)
        return iso

    def get_missing_trades(self):
        # Check missing ones by distinct trade_id

        client = MongoClient('localhost', 27017)
        db = client['Cryptobase']  # the database
        collection = db[f'tickers_{self.product}']  # the collection

        trade_ids = collection.distinct('trade_id')
        trade_ids.sort()
        missing_trades = [i for i in range (trade_ids[0], trade_ids[-1]) if i not in trade_ids]
        print(f'{len(missing_trades)} tickers are missing.')

        trades_to_insert = []
        while len(missing_trades) > 0:
            print('getting_trades')
            trades = self.get_product_trades(after=str(missing_trades[0]+100))
            for trade in trades:
                trade_id = int(trade['trade_id'])
                if trade_id in missing_trades:
                    missing_trades.remove(trade_id)
                    try:
                        date = datetime.strptime(trade['time'],'%Y-%m-%dT%H:%M:%S.%fZ')
                    except ValueError:
                        date = datetime.strptime(trade['time'],'%Y-%m-%dT%H:%M:%SZ')
                    
                    trade_to_insert = {
                        'time': date,
                        'trade_id': trade_id,
                        'price': float(trade['price']),
                        'last_size': float(trade['size']),
                        'side': trade['side'],
                    }
                    trades_to_insert.append(trade_to_insert)
            print(f'{len(missing_trades)} still missing')
            time.sleep(1)

        if len(trades_to_insert) > 0:
            print('Inserting all missing tickers...')
            collection.insert_many(trades_to_insert)

