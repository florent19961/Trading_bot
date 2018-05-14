import asyncio
import websockets
import json
import log
import sqlite3


logger = log.custom_logger('client')
con = sqlite3.connect('../data/crypto.db')
c = con.cursor()


def ticker_handler(msg):
    try:
        ticker = (
            msg['sequence'],
            msg['time'],
            msg['trade_id'],
            msg['product_id'],
            msg['price'],
            msg['open_24h'],
            msg['volume_24h'],
            msg['low_24h'],
            msg['high_24h'],
            msg['volume_30d'],
            msg['best_bid'],
            msg['best_ask'],
            msg['side'],
            msg['last_size']
        )
        with con:
            c.execute(
                'INSERT INTO tickers VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)', ticker)

    except sqlite3.IntegrityError as e:
        logger.error('Could not insert ticker in db : {}'.format(e))
    except Exception as e:
        logger.error(
            'Could not insert ticker in db : {} because of error : {}'.format(msg, e))


async def listen():
    async with websockets.connect("wss://ws-feed.gdax.com") as ws:
        data = json.dumps({"type": "subscribe",
                           "channels": [{"name": "heartbeat", "product_ids": ["BTC-USD"]},
                                        {"name": "ticker", "product_ids": ["BTC-USD"]}]})
        await ws.send(data)

        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=10)
            except asyncio.TimeoutError:
                # No data in 20 seconds, check the connection.
                logger.warning('No data in 10 seconds')
                try:
                    pong_waiter = await ws.ping()
                    await asyncio.wait_for(pong_waiter, timeout=10)
                except asyncio.TimeoutError:
                    # No response to ping in 10 seconds, disconnect.
                    logger.error('No response to ping')
                    break
            else:
                logger.info(msg)
                msg = json.loads(msg)
                if msg['type'] == 'ticker':
                    ticker_handler(msg)


asyncio.get_event_loop().run_until_complete(listen())
