import sched # or scheduler or something that helps
from pymongo import MongoClient
import config
import time
from slackclient import SlackClient
import strategies
from models import Decisions #What's the good way to name it ?
from publicRequests import PublicRequests 
import logging


logger = logging.getLogger('client')
slack_token = config.SLACK_KEY

product = 'BTC-EUR'
def decide():
    #TO DO: use more than one strategy
    strategy = strategies.MLStrategy(product)
    decision = strategy.apply()

    # Save decision in db 
    order_book = PublicRequests(product=product).get_product_order_book(level=2)
    best_bid = order_book['bids'][0][0]
    best_ask = order_book['asks'][0][0]
    Decisions().save_one(decision, strategy.name, order_book)
    # Send decision if not the same to avoid spaming
    if decision != Decisions().get_last():
        send_decision(decision, strategy.name, best_bid, best_ask)

    # TO DO: apply decision
    
    return decision


def post_slack_message(channel, message):
    sc = SlackClient(slack_token)
    sc.api_call("chat.postMessage",
                channel = channel,
                text = message)


def send_decision(decision, strategy_name, bid, ask):
    msg = f'*{product}*: {decision} _({strategy_name})_ \n>{ask}€\n>{bid}€'
    logger.info(f'Bot advice = {msg}')
    post_slack_message('bot_advice', msg)


def get_missing_tickers():
    pr = PublicRequests(product='BTC-EUR')
    pr.get_missing_trades()


if __name__ == '__main__':
    s = sched.scheduler(time.time)
    product = 'BTC-EUR'
    delay = 10 # Delay between decisions in seconds.
    while True:
        if s.empty: # Add an event when the decision has been made.
            s.enter(0,1, get_missing_tickers)
            s.enter(delay, 1, decide)
        s.run()














