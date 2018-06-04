# DB Structure

Each product has its own set of collections.
## Collections

    - decisions_[product]
    - tickers_[product]
    - candles_[product]_[granularity]

    The candles collection is useful for a candle based decision model. However to be faster to react, we should better not use this model and compute aggregates on the tickers collection whenever making a decision (the candles collection becomes obsolete).

### The decisions collection (decisions_product)

    - date (when the candle begins UTC)
    - timestamp (seconds since EPOCH at the beginning of the candle) # Should we ?
    - decision ('Buy', 'Wait', 'Sell')
    - strategy (name of the strategy used to make the decision)

### The tickers collection

    - sequence
    - timestamp
    - trade_id
    - product_id
    - price
    - open_24h
    - volume_24h
    - low_24h
    - high_24h
    - volume_30d
    - best_bid
    - best_ask
    - side
    - last_size

### The candles collection

    - date (when the candle begins UTC)
    - timestamp (seconds since EPOCH at the beginning of the candle)
    - low
    - high
    - opening
    - closing
    - volume

