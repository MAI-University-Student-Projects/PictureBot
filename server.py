import logging
import subprocess
import requests
import time
import json

from flask import Flask, request
from waitress import serve

from telegram import Bot, Update

from config import TOKEN, LOCALHOST_URL

bot = Bot(token=TOKEN)

app = Flask(__name__)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def echo_message(recvd_message):
    chat_id = recvd_message.chat.id
    text = recvd_message.text.encode('utf-8').decode()
    logger.log(level=logging.INFO, msg=f'Got message:{text}')
    bot.sendMessage(chat_id=chat_id, text=text)

def echo_photo(recvd_message):
    chat_id = recvd_message.chat.id
    photo_id = recvd_message.photo[0].file_id
    logger.log(level=logging.INFO, msg=f'Got photo, by id:{photo_id}')
    bot.sendPhoto(chat_id=chat_id, photo=photo_id, caption=recvd_message.caption)

def echo_jpg_png(recvd_message):
    chat_id = recvd_message.chat.id
    file_name = recvd_message.document.file_name.lower()
    if not file_name.endswith(('.jpg', '.png')):
        logger.log(level=logging.INFO, msg=f'Got unsupported document')
        bot.sendMessage(chat_id=chat_id, text='Unsupported picture file type')
    else:
        file_id = recvd_message.document.file_id
        bot.sendDocument(chat_id=chat_id, document=file_id, caption=recvd_message.caption)

@app.route(f'/{TOKEN}', methods=['POST'])
def respond():
    content = Update.de_json(request.get_json(force=True), bot)
    #здесь просматриваем контент и отвечаем
    if content.message:
        if content.message.text:
            echo_message(content.message)
        elif content.message.photo:
            echo_photo(content.message)
        elif content.message.document:
            echo_jpg_png(content.message)
        else:
            logger.log(level=logging.CRITICAL, msg='Unsupported message type')
            bot.sendMessage(chat_id=content.message.chat.id, text='Unsupported message was sent')
    else:
        logger.log(level=logging.INFO, msg='Non-chat update')
    return 'ok, 200'

@app.route('/')
def index():
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
    bot.setWebhook(f'{URL}/{TOKEN}')
    logger.log(level=logging.INFO, msg='webhook established')
    serve(app, host='0.0.0.0', port=5000)