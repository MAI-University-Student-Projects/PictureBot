from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler

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
                    InlineKeyboardButton("send last picture", callback_data='1')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(button_list)
            update.message.reply_text('Time to choose...', reply_markup=reply_markup)
            if update.message.photo:
                self.chat_dict[chat_id] = [ 'photo' ,update.message.photo[0].file_id ]
            else:
                self.chat_dict[chat_id] = [ 'document', update.message.document.file_id ]

    def handle_bot_start(self, update, context):
        chat_id = update.message.chat.id
        self.chat_dict[chat_id] = None
        update.message.reply_text('Hello, I will taunt you echoing your messages and pictures')

    def push_button(self, update, context):
        query = update.callback_query
        chat_id = query.message.chat.id
        query.answer()
        reply = self.chat_dict[chat_id]
        if reply[0] == 'photo':
            query.message.reply_photo(photo=reply[1])
        elif reply[0] == 'document':
            query.message.reply_document(document=reply[1])
        else:
            query.message.reply_text(text='No photo in history')

    def error_message(self, update, context):
        update.message.reply_text('Unsupported message type')
