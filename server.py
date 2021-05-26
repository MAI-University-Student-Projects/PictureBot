import logging
import subprocess
import requests
import time
import json

from flask import Flask, request
from waitress import serve

from telegram import Update

from bot_entity import Telegram_bot
from config import TOKEN, LOCALHOST_URL

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

my_bot = Telegram_bot(TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return 'ok, 200'

@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    content = Update.de_json(request.get_json(force=True), my_bot.updater.bot)
    disp = my_bot.updater.dispatcher
    disp.process_update(content)
    return 'ok, 200'

def get_ngrok_url_init():
    res_url = None
    ngrok_pid = subprocess.Popen(['./ngrok', 'http', '5000'], stdout=None)
    time.sleep(5)
    tunnel_url = requests.get(LOCALHOST_URL).text
    j = json.loads(tunnel_url)
    for url_init in j['tunnels']:
        if url_init['proto'] == 'https':
            res_url = url_init['public_url']
    return res_url

if __name__ == '__main__':
    logger.log(level=logging.INFO, msg='Initialising server')
    URL = get_ngrok_url_init()
    logger.log(level=logging.INFO, msg='Ngrok Server started')
    my_bot.throw_webhook(f'{URL}/{TOKEN}')
    logger.log(level=logging.INFO, msg='webhook established')
    serve(app, host='0.0.0.0', port=5000)