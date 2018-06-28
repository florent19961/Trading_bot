from bokeh.io import output_notebook, show
from bokeh.plotting import figure, output_file


"""Gain function"""
"""gradient = True return the last gain value not the list of the whole evolution"""
def strategy_based_results(decisions_list, market_prices_deltas, fee_rate=0.3, verbose=False, gradient=False):
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
    if not gradient:
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
    elif gradient:
        decisions_results = 100

        for i in range(len(decisions_list)):
            if cash:
                if decisions_list[i] == 1:
                    # Buy
                    cash = False
                    decisions_results = decisions_results * (100 + market_prices_deltas[i] - fee_rate) / 100

            else:
                if decisions_list[i] in [0,1]:
                    # Hold
                    decisions_results = decisions_results * (100 + market_prices_deltas[i]) / 100

                else:
                    # Sell
                    cash = True
                    decisions_results = decisions_results * (100 - fee_rate) / 100
        
        return decisions_results
        

def buy_hold_results(market_prices_deltas):
    market_var = [100]
    for delta in market_prices_deltas:
        market_var.append(market_var[-1] * (100 + delta) / 100)
    return market_var

def plot_strategy_with_labels(labels, decisions, prices, notebook=False, other_lines=[]):
    if notebook:
        output_notebook()
    else:
        output_file("plot.html")
    # the good and bad choices are plotted but not the average
    x_time = [i for i in range(len(prices))]
    x_sell_sell = []
    x_buy_sell = []
    x_sell_buy = []
    x_buy_buy = []
    y_sell_sell = []
    y_buy_sell = []
    y_sell_buy = []
    y_buy_buy = []
    for i in range(len(labels)):
        if labels[i] == -1 and decisions[i] == -1: # sell/sell (label/prediction)
            x_sell_sell.append(i)
            y_sell_sell.append(prices[i])
        elif labels[i] == -1 and decisions[i] == 1: # sell/buy
            x_sell_buy.append(i)
            y_sell_buy.append(prices[i])
        elif labels[i] == 1 and decisions[i] == -1: # buy/sell
            x_buy_sell.append(i)
            y_buy_sell.append(prices[i])
        elif labels[i] == 1 and decisions[i] == 1: # buy/buy
            x_buy_buy.append(i)
            y_buy_buy.append(prices[i])
            
    p = figure(plot_width=800, plot_height=600, title='Decisions, labels and price',
               x_axis_label='Time', y_axis_label='Price')

    p.line(x_time, prices, legend='Price', line_alpha=0.2)
    for line in other_lines:
        p.line(x_time, line['data'], legend=line['legend'], line_alpha=0.2)

    p.inverted_triangle(x_sell_sell, y_sell_sell, legend='should sell -> sell', size=8,
                        line_color="mediumseagreen", fill_color="mediumseagreen", fill_alpha=0.5)
    p.inverted_triangle(x_sell_buy, y_sell_buy, legend='should sell -> buy',
                        size=8, line_color="crimson", fill_color="crimson", fill_alpha=0.5)
    p.triangle(x_buy_sell, y_buy_sell, size=8, legend='should buy -> sell',
               line_color="crimson", fill_color="crimson", fill_alpha=0.5)
    p.triangle(x_buy_buy, y_buy_buy, size=8, legend='should buy -> buy',
               line_color="mediumseagreen", fill_color="mediumseagreen", fill_alpha=0.5)
    show(p)


def plot_strategy(decisions, prices, notebook=False, other_lines=[]):
    if notebook:
        output_notebook()
    else:
        output_file("plot.html")
    x_time = [i for i in range(len(prices))]

    x_sell = []
    x_buy = []
    y_sell = []
    y_buy = []
    for i in range(len(decisions)):
        if decisions[i] == -1:
            x_sell.append(i)
            y_sell.append(prices[i])
        elif decisions[i] == 1:
            x_buy.append(i)
            y_buy.append(prices[i])
 
            
    results_plot = figure(plot_width=800, plot_height=600, title='Decisions and price',
               x_axis_label='Time', y_axis_label='Price')

    results_plot.line(x_time, prices, legend='Price', line_alpha=0.4)
    for line in other_lines:
        results_plot.line(x_time, line['data'], legend=line['legend'], line_alpha=0.2)

    results_plot.circle(x_sell, y_sell, legend='Sell', size=8,line_color="crimson", fill_color="crimson", fill_alpha=0.5)
    results_plot.circle(x_buy, y_buy, size=8, legend='Buy',line_color="mediumseagreen", fill_color="mediumseagreen", fill_alpha=0.5)
    show(results_plot)

"""
How to use this:

from results import strategy_based_results
from results import buy_hold_results

strategy = [1, 1, 0, 1, -1, 1, 0, 0, -1, 1]
market_var = [100, 100, -50 , 0, 50, 50, 20, -20, 30, 5]

strategy_based_results(strategy, market_var, fee_rate=0.3, verbose=True)
buy_hold_results(market_var)

"""

