from models import Candles


class Macd():
    def __init__(self, product):
        self.name = 'macd'
        self.product = product

    def __compute(self, last26):
        #last26 should be sorted from the oldest to the newest
        def mme(last_prices):
            c = 2 / (len(last_prices)+1)
            k = 0
            result = 0
            for x in reversed(last_prices):
                result += float(x) * (1 - c) ** k
                k += 1
            return result * c

        return mme(last26[14:25]) - mme(last26)

    def apply(self):
        last_candles = Candles(self.product).get_last_candles_price_list(3600,26)
        macd = self.__compute(last_candles)

        if macd > 0:
            return 'Buy'
        elif macd < 0:
            return 'Sell'
        else:
            return 'Wait'


# -------------------------------------
# -----  ADD NEW STRATEGIES HERE  -----
# -- IT SHOULD BE BUILT THE SAME WAY --
# -------------------------------------


