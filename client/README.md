# DB Structure


## Collections

    - decision
    - trades
    - candles

### The decisions collection (decisions_product)

    - time (when the candle begins in UTC)
    - product_id ('BTC-EUR', 'ETH-EUR', 'LTC-EUR', 'BCH-EUR')
    - decision ('Buy', 'Wait', 'Sell')
    - strategy (the name of the strategy used to make the decision)
    - order_book (snapshot of the order boook at that time)

### The trades collection

    - trade_id
    - time
    - product_id
    - size
    - price
    - side ('buy', 'sell')
    - ticker_data (data from the ticker if available)

### The candles collection

    - date (when the candle begins UTC)
    - timestamp (seconds since EPOCH at the beginning of the candle)
    - low
    - high
    - opening
    - closing
    - volume

