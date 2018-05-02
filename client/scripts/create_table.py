import sqlite3

conn = sqlite3.connect('../data/crypto.db')
c = conn.cursor()
c.execute('''CREATE TABLE tickers (
    sequence integer,
    time text,
    trade_id integer,
    product_id text,
    price real,
    open_24h real,
    volume_24h real,
    low_24h real,
    high_24h real,
    volume_30d real,
    best_bid real,
    best_ask real,
    side text,
    last_size real)''')

conn.commit()
conn.close()




