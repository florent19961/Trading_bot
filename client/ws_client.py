import asyncio
import websockets
import json
import sqlite3
import customlog
import models


logger = customlog.custom_logger('client')
product = 'BTC-EUR'


async def listen(product='BTC-EUR'):
    async with websockets.connect("wss://ws-feed.gdax.com") as ws:
        data = json.dumps({"type": "subscribe",
                           "channels": [{"name": "heartbeat", "product_ids": [product]},
                                        {"name": "ticker", "product_ids": [product]}]})
        await ws.send(data)

        has_subscribed = False
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=10)
            except asyncio.TimeoutError:
                # No data in 10 seconds, check the connection.
                logger.warning('No data in 10 seconds')
                try:
                    pong_waiter = await ws.ping()
                    await asyncio.wait_for(pong_waiter, timeout=10)
                except asyncio.TimeoutError:
                    # No response to ping in 10 seconds, disconnect.
                    logger.error('No response to ping, shut off...')
                    break
            else:
                logger.info(msg)
                msg = json.loads(msg)
                if msg['type'] == 'ticker' and has_subscribed:
                    models.Ticker(msg).save_one()
                elif msg['type'] == 'subscriptions':
                    has_subscribed = True



asyncio.get_event_loop().run_until_complete(listen(product))
