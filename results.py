def strategy_based_results(decisions_list, market_prices_deltas, fee_rate=0.3, verbose=False):
    """
    Returns the list of successive gains.
    Prints other info like number of hold, buy, sell, free_cash, fee costs.
    """

    cash = True
    decisions_results = [100]
    fees_cost = 0
    got_cash = 0
    buy_decisions = 0
    sell_decisions = 0
    hold_decisions = 0

    for i in range(len(decisions_list)):

        if decisions_list[i] == 1 and cash:
            # Buy
            cash = False
            decisions_results.append(
                decisions_results[-1]*(100 + market_prices_deltas[i] - fee_rate) / 100)
            fees_cost += decisions_results[-1] * fee_rate / 100
            buy_decisions += 1
            got_cash += 1

        elif decisions_list[i] == -1 and cash:
            # Wait
            decisions_results.append(decisions_results[-1])
            got_cash += 1

        elif decisions_list[i] == 0 and cash:
            # Wait
            decisions_results.append(decisions_results[-1])
            got_cash += 1

        elif decisions_list[i] == 0 and not cash:
            # Hold
            decisions_results.append(
                decisions_results[-1] * (100 + market_prices_deltas[i]) / 100)
            hold_decisions += 1

        elif decisions_list[i] == -1 and not cash:
            # Sell
            cash = True
            decisions_results.append(
                decisions_results[-1] * (100 - fee_rate) / 100)
            fees_cost += decisions_results[-1] * fee_rate / 100
            sell_decisions += 1

        elif decisions_list[i] == 1 and not cash:
            # Hold
            decisions_results.append(
                decisions_results[-1] * (100 + market_prices_deltas[i]) / 100)
            hold_decisions += 1

        else:
            raise Exception

    if verbose:
        print('Aggregated results are:')
        print('Hold         : {}'.format(hold_decisions))
        print('Buy          : {}'.format(buy_decisions))
        print('Sell         : {}'.format(sell_decisions))
        print('Got_cash     : {}'.format(got_cash))
        print('Fees_cost    : {}% of initial investment'.format(fees_cost))
        print('Total_result : {0:+}% from initial investment'.format(decisions_results[-1] - 100))

    return decisions_results

def buy_hold_results(market_prices_deltas):
    market_var = [100]
    for delta in market_prices_deltas:
        market_var.append(market_var[-1] * (100 + delta) / 100)
    return market_var




"""
How to use this:

from results import strategy_based_results
from results import buy_hold_results

strategy = [1, 1, 0, 1, -1, 1, 0, 0, -1, 1]
market_var = [100, 100, -50 , 0, 50, 50, 20, -20, 30, 5]

strategy_based_results(strategy, market_var, fee_rate=0.3, verbose=True)
buy_hold_results(market_var)

"""

