from models import Tickers


class Macd():
    def __init__(self):
        self.name = 'macd'

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
        last_candles = Tickers().get_last_candles(3600,'BTC-EUR',26) # to implement
        macd = self.__compute(last_candles)

        if macd > 0:
            return 1
        elif macd < 0:
            return -1
        else:
            return 0


# -------------------------------------
# -----  ADD NEW STRATEGIES HERE  -----
# -- IT SHOULD BE BUILT THE SAME WAY --
# -------------------------------------


