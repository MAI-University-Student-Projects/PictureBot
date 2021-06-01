import os
import requests

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler
from PIL import Image, ImageFilter

class Telegram_bot:
    def __init__(self, token):
        self.updater = Updater(token=token)
        msg_filt = Filters.document.file_extension('jpg') | Filters.document.file_extension('png') \
                   | Filters.photo | Filters.caption \
                   | Filters.text & (~Filters.command)

        self.updater.dispatcher.add_handler(MessageHandler(filters=msg_filt, callback=self.handle_message))
        self.updater.dispatcher.add_handler(MessageHandler(filters=(~msg_filt) & (~Filters.command), callback=self.error_message))
        self.updater.dispatcher.add_handler(CommandHandler(command='start', callback=self.handle_bot_start))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(callback=self.push_button))

        self.chat_dict = {}

    def throw_webhook(self, url):
        self.updater.bot.setWebhook(url=url)

    def handle_message(self, update, context):
        chat_id = update.message.chat.id
        if update.message.text:
            text = update.message.text.encode('utf-8').decode()
            update.message.reply_text(text=text)
        else:
            button_list = [
                [
                    InlineKeyboardButton("Blur", callback_data='blur'),
                    InlineKeyboardButton("Grayscale", callback_data='gray')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(button_list)
            update.message.reply_text('Time to choose...', reply_markup=reply_markup)
            if update.message.photo:
                self.chat_dict[chat_id] = {'type': 'photo', 'id': update.message.photo[0].file_id }
            else:
                self.chat_dict[chat_id] = {'type': 'document', 'id': update.message.document.file_id}

    def handle_bot_start(self, update, context):
        chat_id = update.message.chat.id
        self.chat_dict[chat_id] = None
        update.message.reply_text('Hello, I will taunt you echoing your messages and pictures')

    def push_button(self, update, context):
        query = update.callback_query
        chat_id = query.message.chat.id
        query.answer()
        try:
            reply_pic = self.chat_dict[chat_id]
            pic_info = self.updater.bot.get_file(file_id=reply_pic['id'])
            img = Image.open(fp=requests.get(pic_info.file_path, stream=True).raw)#
            if query.data == 'blur':
                new_img = img.convert('RGB').filter(ImageFilter.GaussianBlur(radius=4))
            else:
                new_img = img.convert('LA')
            new_img.save('img.png')
            with open('img.png', 'rb') as f:
                query.message.reply_photo(photo=f)
            os.remove('img.png')
        except KeyError:
            query.message.reply_text(text='No photo in button')

    def error_message(self, update, context):
        update.message.reply_text('Unsupported message type')
