from telegram.ext import Updater, MessageHandler, CommandHandler, Filters

class Telegram_bot:
    def __init__(self, token):
        self.updater = Updater(token=token)
        msg_filt = Filters.document.file_extension("jpg") | Filters.document.file_extension("png") \
                   | Filters.photo | Filters.caption \
                   | Filters.text & (~Filters.command)
        msg_handler = MessageHandler(filters=msg_filt, callback=self.handle_message)
        err_handler = MessageHandler(filters=(~msg_filt) & (~Filters.command), callback=self.error_message)
        cmd_handler = CommandHandler(command='start', callback=self.handle_bot_start)
        self.updater.dispatcher.add_handler(msg_handler)
        self.updater.dispatcher.add_handler(err_handler)
        self.updater.dispatcher.add_handler(cmd_handler)

        self.chat_dict = {}

    def throw_webhook(self, url):
        self.updater.bot.setWebhook(url=url)

    def handle_message(self, update, context):
        chat_id = update.message.chat.id
        if update.message.text:
            text = update.message.text.encode('utf-8').decode()
            update.message.reply_text(text=text)
        else:
            if update.message.photo:
                self.chat_dict[chat_id] = update.message.photo[0].file_id
                update.message.reply_photo(photo=self.chat_dict[chat_id], caption=update.message.caption)
            else:
                self.chat_dict[chat_id] = update.message.document.file_id
                update.message.reply_document(document=self.chat_dict[chat_id], caption=update.message.caption)

    def handle_bot_start(self, update, context):
        chat_id = update.message.chat.id
        self.chat_dict[chat_id] = None
        update.message.reply_text('Hello, I will taunt you echoing your messages and pictures')

    def error_message(self, update, context):
        chat_id = update.message.chat.id

        update.message.reply_text('Unsupported message type')

# нужны ответы пользователю о плохих данных, либо убрать фильтры, либо писать свой фильтр