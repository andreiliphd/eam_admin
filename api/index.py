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

def telegram_url_builder(method, **kwargs):
    basic = "https://api.telegram.org/bot" + os.getenv("TOKEN") + "/" + str(method) + "?"
    for k, val in kwargs.items():
        print("%s == %s" % (k, val))
        basic += str(k) + "=" + str(val) + "&"
    basic = basic[0:len(basic) - 1]
    r = requests.get(basic)
    logger.log(logging.WARNING, str(r)) 
    logger.log(logging.WARNING, str(basic)) 
    return basic

@app.route("/", methods = ["GET", "POST"])
def entry():
    data = request.json
    keys = redis.keys('*')
    values = redis.mget(keys)
    inline = {"inline_keyboard" : []}
    for i in range(len(keys)):
        inline['inline_keyboard'].append([{"text": redis.get(keys[i]), "callback_data": keys[i]}])
    telegram_url_builder("sendMessage", chat_id=data["message"]["chat"]["id"], text = "Утвердить", reply_markup = inline)
    logger.log(logging.WARNING, str(data))
    return {"text": str(data)}
