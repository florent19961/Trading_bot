from models import Candles
import numpy as np
import json
import pickle
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

class Calculus():
    def __init__(self, product, granularity=3600):
        self.last_candles = Candles(product).get_last_candles(granularity,30)
        self.last_prices = [c['close'] for c in self.last_candles]

    def __mme(self,last_prices):
        c = 2 / (len(last_prices)+1)
        k = 0
        result = 0
        for x in (last_prices):
            result += float(x) * (1 - c) ** k
            k += 1
        return result * c

    def __bdb_high(self,last20):
        mean = np.mean(last20)
        sigma = np.std(last20, 0)
        return mean + sigma
    
    def __bdb_low(self,last20):
        mean = np.mean(last20)
        sigma = np.std(last20, 0)
        return mean - sigma

    def bdb_high(self):
        return self.__bdb_high(self.last_prices[:19])
        
    def bdb_low(self):
        return self.__bdb_low(self.last_prices[:19])

    def __macd(self, last26):
        return self.__mme(last26[:11]) - self.__mme(last26)

    def macd(self):
        return self.__macd(self.last_prices[:25])

    def macd_1(self):
        return self.__macd(self.last_prices[1:26])

    def macd_2(self):
        return self.__macd(self.last_prices[2:27])

    def macd_3(self):
        return self.__macd(self.last_prices[3:28])

    def macd_derivative(self):
        return self.macd() - self.macd_1()

    def macd_second_derivative(self):
        return self.macd() - self.macd_1()

    def last_price(self):
        return self.last_prices[0]

    def opening_price(self, ):
        return self.last_candles[0]['open']
    
    def high_price(self):
        return self.last_candles[0]['max']

    def low_price(self):
        return self.last_candles[0]['min']

    def delta(self):
        return self.last_prices[0] - self.last_prices[1]

    def delta_1(self):
        return self.last_prices[1] - self.last_prices[2]

    def delta_2(self):
        return self.last_prices[2] - self.last_prices[3]

    def volatility(self):
        return self.high_price() - self.low_price()

    def d_macd_macd_product(self):
        return self.macd_derivative() * self.macd()

    def derivate_volatility(self):
        return self.volatility() - (self.last_candles[1]['max'] - self.last_candles[1]['min'])

    def volume_derivative(self):
        return self.last_candles[0]['volume'] - self.last_candles[1]['volume']
    
    def stochastic(self):
        if self.high_price() - self.low_price() == 0:
            return 0
        else:
            return (self.last_price() - self.low_price()) / (self.high_price() - self.low_price())

    def stochastic_1(self):
        close = self.last_candles[1]['close']
        min = self.last_candles[0]['min']
        max = self.last_candles[0]['max']
        if (max - min) == 0:
            return 0
        else:
            return (close - min) / (max - min)

    def stochastic_derivative(self):
        return self.stochastic() - self.stochastic_1()
    
    def d_stoch_stoch_product(self):
        return self.stochastic_derivative() * self.stochastic()


class Macd():
    def __init__(self, product):
        self.name = 'macd'
        self.product = product

    def __compute(self):
        #last26 should be sorted from the newest to the oldest
        return Calculus(self.product, 3600).macd()

    def apply(self):
        macd = self.__compute()
        if macd > 0:
            return 'Buy'
        elif macd < 0:
            return 'Sell'
        else:
            return 'Wait'


class MLStrategy():
    def __init__(self, product):
        self.name = 'Machine Learning Strategy'
        self.product = product
    
    def __compute(self):
        c = Calculus(self.product, 3600)
        price = c.last_price()
        cols = {
            'bdb_high_n':               c.bdb_high() / price, 
            'bdb_low_n':                c.bdb_low() / price,
            'macd_n':                   c.macd() / price,
            'macd_derivative_n':        c.macd_derivative() / price,
            'variation':                c.delta() / price * 100,
            'opening_price':            c.opening_price() / price,
            'high_price_n':             c.high_price() / price,
            'low_price_n':              c.low_price() / price,
            'macd-1':                   c.macd_1() / price,
            'macd-2':                   c.macd_2() / price,
            'macd-3':                   c.macd_3() / price, 
            'var-1':                    c.delta_1() / price * 100,
            'var-2':                    c.delta_2() / price * 100,
            'macd_second_derivative_n': c.macd_second_derivative() / price,
            'product_macd':             c.d_macd_macd_product() / price ** 2,
            'volatility':               c.volatility() / price,
            'derivate_volatility':      c.derivate_volatility() / price,
            'derivate_volume':          c.volume_derivative(),
            'stochastic_derivative':    c.stochastic_derivative(),
            'product_stochastic':       c.d_stoch_stoch_product(),
            'stochastic':               c.stochastic()
            }
        return cols


    def apply(self):
        cols = self.__compute()
        values = []
        for value in cols.values():
            values.append(value)
        array = np.array(values)

        # Standard Scaler's parameters loading
        mean = pickle.load(open("mean.p", "rb"))
        std = pickle.load(open( "std.p", "rb"))

        # Standard Scaler's reconstruction
        scaler = StandardScaler(copy=False)
        scaler.mean_ = mean
        scaler.std_ = std

        # fit_transform data
        X = scaler.fit_transform(array)

        # PCA Loading
        pca = pickle.load( open( "pca.p", "rb" ) )

        # Transformation test and train data from PCA loaded
        X = pca.transform(X)

        ### 3rd step
        ## Prediction

        clf = pickle.load( open( "clf.p", "rb" ) )
        prediction = clf.predict(X)
        print(json.dumps(cols, indent=4))
        if prediction == 0:
            return 'Sell'
        elif prediction == 1:
            return 'Buy'
        else:
            return 'error'
    
        



# -------------------------------------
# -----  ADD NEW STRATEGIES HERE  -----
# -- IT SHOULD BE BUILT THE SAME WAY --
# -------------------------------------


