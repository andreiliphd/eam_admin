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

def telegram_url_builder(method, payload):
    basic = "https://api.telegram.org/bot" + "7881036983:AAGHguPzNqEh3StCC8l1iTsXzZDqKtAQcwI" + "/" + method
    r = requests.post(basic, data = payload)
    logger.log(logging.WARNING, str(r.text))
    print(r.status_code)
    print(r.text)
    return basic

@app.route("/", methods = ["GET", "POST"])
def entry():
    data = request.json
    if "message" in data.keys():
        keys = redis.keys('*')
        values = redis.mget(keys)
        inline = {"inline_keyboard" : []}
        for i in range(len(keys)):
            inline['inline_keyboard'].append([{"text": redis.get(keys[i]), "callback_data": keys[i]}])
        outline = json.dumps(inline) 
        telegram_url_builder("sendMessage", {"chat_id": data["message"]["chat"]["id"], "text": "Утвердить", "reply_markup": outline})
        logger.log(logging.WARNING, str(data))
    else:
        logger.log(logging.WARNING, str(data))
    return {"text": str(data)}
