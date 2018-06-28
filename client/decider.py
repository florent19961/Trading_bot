import sched # or scheduler or something that helps
from pymongo import MongoClient
import config
import time
from slackclient import SlackClient
import strategies
from models import Decision 
from publicRequests import PublicRequests 
import logging


logger = logging.getLogger('client')
SLACK_TOKEN = config.SLACK_KEY
PRODUCT = 'BTC-EUR'

def decide():
    #TO DO: use more than one strategy
    strategy = strategies.MLStrategy(PRODUCT)
    decision = strategy.get_decision()

    # Get order_book
    order_book = PublicRequests(product=PRODUCT).get_product_order_book(level=2)
    best_bid = order_book['bids'][0][0]
    best_ask = order_book['asks'][0][0]
    decision.order_book = order_book
    
    # Send decision if not the same to avoid spaming
    # if decision.decision != Decision.objects.last_decision():
    #    send_decision(decision, strategy.name, best_bid, best_ask)

    # Save decision
    decision.save()

    # TO DO: apply decision
    


def post_slack_message(channel, message):
    sc = SlackClient(SLACK_TOKEN)
    sc.api_call("chat.postMessage",
                channel = channel,
                text = message)


def send_decision(decision, strategy_name, bid, ask):
    msg = f'*{PRODUCT}*: {decision} _({strategy_name})_ \n>{ask}€\n>{bid}€'
    logger.info(f'Bot advice = {msg}')
    post_slack_message('bot_advice', msg)


def get_missing_trades():
    pr = PublicRequests(product=PRODUCT)
    pr.get_missing_trades()


if __name__ == '__main__':
    s = sched.scheduler(time.time)
    delay = 10 # Delay between decisions in seconds.
    while True:
        if s.empty: # Add an event when the decision has been made.
            s.enter(0,1, get_missing_trades)
            s.enter(delay, 1, decide)
        s.run()














