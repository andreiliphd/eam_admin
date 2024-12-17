import json
import os
import requests
import logging
from flask import Flask, request
from upstash_redis import Redis

app = Flask(__name__)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

redis = Redis(url=os.getenv("HOST_REDIS"), token=os.getenv("PASSWORD_REDIS"))

def display_all_options_message(data):
    keys = redis.keys('*')
    values = redis.mget(keys)
    inline = {"inline_keyboard" : []}
    for i in range(len(keys)):
        inline['inline_keyboard'].append([{"text": redis.get(keys[i]), "callback_data": keys[i]}])
    outline = json.dumps(inline) 
    telegram_url_builder("sendMessage", {"chat_id": os.getenv("ADMIN_CHAT_ID"), "text": "Утвердить", "reply_markup": outline})
    logger.log(logging.WARNING, "display_all_opptions" + " " + str(data))
    return {"text": str(data)}

def display_all_opptions_data(data):
    keys = redis.keys('*')
    values = redis.mget(keys)
    inline = {"inline_keyboard" : []}
    for i in range(len(keys)):
        inline['inline_keyboard'].append([{"text": redis.get(keys[i]), "callback_data": keys[i]}])
    outline = json.dumps(inline) 
    telegram_url_builder("sendMessage", {"chat_id": os.getenv("ADMIN_CHAT_ID"), "text": "Утвердить", "reply_markup": outline})
    logger.log(logging.WARNING, "display_all_opptions" + " " + str(data))
    return {"text": str(data)}

def telegram_url_builder(method, payload):
    basic = "https://api.telegram.org/bot" + "7881036983:AAGHguPzNqEh3StCC8l1iTsXzZDqKtAQcwI" + "/" + method
    r = requests.post(basic, data = payload)
    logger.log(logging.WARNING, "telegram_url_builder" + " " + str(r.text))
    return basic

@app.route("/", methods = ["GET", "POST"])
def entry():
    data = request.json
    if "message" in data.keys():
        display_all_options_message(data)
    elif ("callback_query" in data.keys()) & ("data" in data["callback_query"].keys()):
        telegram_url_builder("sendMessage", {"chat_id": os.getenv("RL_CHAT_ID"), "text": redis.get(data["callback_query"]["data"])})
        redis.delete(data["callback_query"]["data"])
        display_all_opptions_data(data)
        
    else:
        logger.log(logging.WARNING, str(data))
    return {"text": str(data)}
