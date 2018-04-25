def macd(self, data_row):
    """
    Returns 0 for hold, 1 for buy, -1 for sell.
    """

    macd = data_row['macd']
    macd_derivative = data_row['macd_derivative_n']
    macd_second_derivative = data_row['macd_second_derivative']
    if macd >= 0:
        if macd_derivative >= 0 and macd_second_derivative >= 0:
            return 1
        else:
            return 0
    else:
        return -1
