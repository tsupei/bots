import logging
import os
import sys
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler

logger = logging.getLogger('inspection')

def _get_mrt_data():
    mrt_data = dict()
    with open("./mrt.txt", 'r', encoding='utf8') as file:
        lines = file.read().split('\n')
        for line in lines:
            entries = line.split('\t')
            if len(entries) == 3:
                logger.info("MRT Station {} is added".format(entries[0]))
                mrt_data.setdefault(entries[0], dict())
                mrt_data[entries[0]][entries[1]] = int(entries[2])
    return mrt_data

# Entry Point
def mrt(update, context):
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name, _ in mrt_data.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("🙂請選擇要設定的捷運線", reply_markup=reply_markup)
    return "MRTLINE"

# First State: Choose MRT line
def mrt_line(update, context):
    query = update.callback_query
    query.answer()
    mrtline_name = query.data
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name, _ in mrt_data[mrtline_name].items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="😆選擇了捷運線，再來選擇「{}」的捷運站點".format(mrtline_name), reply_markup=reply_markup)
    context.chat_data["mrtline"] = mrtline_name 
    return "MRTSTATION"

# Second State: Choose MRT Station
def mrt_station(update, context):
    query = update.callback_query
    query.answer()
    mrt_station = query.data
    query.edit_message_text(text="🧐已設定尋找「{}」附近的租屋點".format(mrt_station))
    context.chat_data["mrt_station"] = mrt_station 
    return -1

mrt_data = _get_mrt_data()

mrt_conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('mrt', mrt)],
        states = {
            "MRTLINE": [CallbackQueryHandler(mrt_line)],
            "MRTSTATION": [CallbackQueryHandler(mrt_station)]
            },
        fallbacks=[CommandHandler('mrt', mrt)])
