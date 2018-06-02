import sched # or scheduler or something that helps
from pymongo import MongoClient
import config
import time
from slackclient import SlackClient
import strategies
from models import Decisions #What's the good way to name it ? 

slack_token = config.SLACK_KEY


def decide():
    #TO DO: use more than one strategy
    strategy = strategies.Macd()
    decision = strategy.apply()
    # Save decision in db 
    
    # Send decision if not the same to avoid spaming
    if decision != Decisions().get_last():
        send_decision(decision, strategy.name)
    # TO DO:take decision
    return decision


def post_slack_message(channel, message):
    sc = SlackClient(slack_token)
    sc.api_call("chat.postMessage",
                channel = channel,
                text = message)


def send_decision(decision, strategy_name):
    if decision == 1:
        decision_str = 'Buy'
    elif decision == -1:
        decision_str = 'Sell'
    else:
        decision_str = 'Don\'t move !'
    msg = f'*{product}*: {decision_str} ({strategy_name})'
    post_slack_message('bot_advice', msg)


if __name__ == '__main__':
    s = sched.scheduler(time.time)
    product = 'BTC-EUR'
    delay = 60 # Delay between decisions in seconds.
    while True:
        if s.empty: # Add an event when the decision has been made. 
            s.enter(delay, 1, decide)
        s.run()














