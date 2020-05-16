import logging
import os
import sys
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton
from commands import mrt_conversation_handler 

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def start(update, context):
    welcome_message = "Hello!"
    keyboard = [[KeyboardButton(name, callback_data=name)] for name in ["/mrt", "/price"]]
    reply_markup = ReplyKeyboardMarkup(keyboard) 
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message, reply_markup=reply_markup)

def start_buttons(update, context):
    query = update.callback_query
    query.answer()
    command = query.data
    

if __name__ == "__main__":
    # Get bot-token from enviroment variable
    bot_token = os.environ["bot_token"]

    # Load Basic Information

    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    dispatcher.add_handler(mrt_conversation_handler)

    updater.start_polling()
    updater.idle()

