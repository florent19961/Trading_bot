def strategy_based_results(self, decisions_list, market_prices_deltas, fee_rate=0.3):
    """
    Returns the list of successive gains.
    Prints other info like number of hold, buy, sell, free_cash, fee costs.
    """

    cash = True
    decisions_results = [100]
    fees_cost = [100]
    free_cash = 0
    achat = 0
    vente = 0
    hold = 0

    for i in range(len(decisions_list)):

        if decisions_list[i] == 1 and cash:
            # Buy
            cash = False
            decisions_results.append(
                decisions_results[-1]*(100 + market_prices_deltas[i] - fee_rate) / 100)
            fees_cost.append(
                fees_cost[-1] + decisions_results[-1] * fee_rate / 100)
            achat += 1

        elif decisions_list[i] == -1 and cash:
            # Wait
            decisions_results.append(decisions_results[-1])
            free_cash += 1

        elif decisions_list[i] == 0 and cash:
            # Wait
            decisions_results.append(decisions_results[-1])
            free_cash += 1

        elif decisions_list[i] == 0 and not cash:
            # Hold
            decisions_results.append(
                decisions_results[-1] * (100 + market_prices_deltas[i]) / 100)
            hold += 1

        elif decisions_list[i] == -1 and not cash:
            # Sell
            cash = True
            decisions_results.append(
                decisions_results[-1] * (100 - fee_rate) / 100)
            fees_cost.append(
                fees_cost[-1] + decisions_results[-1] * fee_rate / 100)
            vente += 1

        elif decisions_list[i] == 1 and not cash:
            # Hold
            decisions_results.append(
                decisions_results[-1] * (100 + market_prices_deltas[i]) / 100)
            hold += 1

        else:
            raise Exception

    # print(hold, achat, vente, free_cash, fees_cost)
    return decisions_results

def buy_hold_results(self, market_prices_deltas):
    market_var = [100]
    for delta in market_prices_deltas:
        market_var.append(market_var[-1] * (100 + delta) / 100)
    return market_var




"""
How to use this:

df['macd_decision'] =  df.apply(Strategies.macd, axis=1)

decisions_list = df['macd_decision'].toList()
market_prices = df['prices'].toList()
Results.decisions_results(decisions_list, market_var, fee_rate = 0.3)

"""

