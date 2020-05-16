import logging
import os
import sys
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler
from telegram.ext import MessageHandler, Filters
from crawler import HouseCrawler



logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

mrt_data = dict()
floormap_data = dict()

def _read_mrt():
    with open("./mrt.txt", 'r', encoding='utf8') as file:
        lines = file.read().split('\n')
        for line in lines:
            entries = line.split('\t')
            if len(entries) == 3:
                logging.info("MRT STation {} is added".format(entries[0]))
                mrt_data.setdefault(entries[0], dict())
                mrt_data[entries[0]][entries[1]] = int(entries[2])

def _read_floormap():
    with open("./floormap.txt", 'r', encoding='utf8') as file:
        lines = file.read().split('\n')
        for line in lines:
            entries = line.split('\t')
            if len(entries) == 2:
                logging.info("Floormap {} is added".format(entries[0])) 
                floormap_data[entries[0]] = int(entries[1])

def start(update, context):

    welcome_message = '''
    🤗 哈囉! 歡迎使用租屋監測機器人
    /search - 根據設定條件，搜尋租屋
    /condition - 查詢目前的設定條件
    /inspect - 根據設定條件，派出機器人進行監控
    /mrt - 設定捷運站
    /price - 設定價錢
    /floor - 設定樓層限制
    /floormap - 設定格局
    '''
    context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_message)

# def echo(update, context):
#     context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def mrt(update, context):
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name, _ in mrt_data.items()]
    # keyboard = [InlineKeyboardButton("TEST", callback_data="TEST")]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('請選擇要設定的捷運線', reply_markup=reply_markup)
    return "MRTLINE"

def mrtline(update, context):
    query = update.callback_query
    query.answer()
    mrtline_name = query.data
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name, _ in mrt_data[mrtline_name].items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="選擇{}的捷運站點".format(mrtline_name), reply_markup=reply_markup)
    context.chat_data["mrtline"] = mrtline_name 
    return "MRTSTATION"

def mrt_station(update, context):
    query = update.callback_query
    query.answer()
    mrt_station = query.data
    query.edit_message_text(text="已設定尋找「{}」附近的租屋點".format(mrt_station))
    context.chat_data["mrt_station"] = mrt_station 
    return -1

def floormap(update, context):
    keyboard = [[InlineKeyboardButton(name, callback_data=name)] for name, _ in floormap_data.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('請選擇要設定的租房類型', reply_markup=reply_markup)

def floormap_button(update, context):
    query = update.callback_query
    query.answer()
    floormap = query.data
    query.edit_message_text(text="已設定為「{}」類型的租屋處".format(floormap))
    context.chat_data["floormap"] = floormap
    
def price(update, context):
    keyboard = [[InlineKeyboardButton("{}".format(price), callback_data=price)] for price in range(0, 50000, 5000)]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("請選擇租屋價格下限", reply_markup=reply_markup)
    return "LOWER_PRICE"

def lower_price(update, context):
    query = update.callback_query
    query.answer()
    
    lower_price = int(query.data)
    
    keyboard = [[InlineKeyboardButton("{}".format(price), callback_data=price)] for price in range(lower_price, 50000, 5000)]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text("請選擇租屋價格上限", reply_markup=reply_markup)
    context.chat_data["price_lower_bound"] = lower_price
    return "UPPER_PRICE"

def upper_price(update, context):
    query = update.callback_query
    query.answer()
    
    upper_price = int(query.data)
    
    lower_price = int(context.chat_data["price_lower_bound"])
    
    if lower_price <= upper_price:
        context.chat_data["price_upper_bound"] = upper_price
        query.edit_message_text("完成價格設定，尋找價格區間{}~{}的租屋處".format(context.chat_data["price_lower_bound"], context.chat_data["price_upper_bound"]))
        return -1 # End the conversion
    return 

def condition(update, context):
    chat_data = context.chat_data
    
    # Default settings
    chat_data.setdefault("mrt_station", None)
    chat_data.setdefault("price_lower_bound", None)
    chat_data.setdefault("price_upper_bound", None)
    chat_data.setdefault("floormap", None)

    conditions = []
    if chat_data["mrt_station"]:
        conditions.append("捷運站： {}".format(chat_data["mrt_station"]))
    else:
        conditions.append("捷運站： 不指定")

    if chat_data["price_lower_bound"] is not None and chat_data["price_upper_bound"] is not None:
        conditions.append("價格範圍： {} ~ {}".format(chat_data["price_lower_bound"], chat_data["price_upper_bound"]))
    else:
        conditions.append("價格範圍： 不指定")
    
    if chat_data["floormap"]:
        conditions.append("格局： {}".format(chat_data["floormap"]))
    else:
        conditions.append("格局： 不指定")

    update.message.reply_text("\n".join(conditions))
    

def search(update, context):
    chat_data = context.chat_data
    
    # Default settings
    chat_data.setdefault("mrt_station", None)
    chat_data.setdefault("price_lower_bound", None)
    chat_data.setdefault("price_upper_bound", None)
    chat_data.setdefault("floormap", None)

    conditions = []
    if chat_data["mrt_station"]:
        conditions.append("捷運站： {}".format(chat_data["mrt_station"]))
    else:
        conditions.append("捷運站： 不指定")

    if chat_data["price_lower_bound"] is not None and chat_data["price_upper_bound"] is not None:
        conditions.append("價格範圍： {} ~ {}".format(chat_data["price_lower_bound"], chat_data["price_upper_bound"]))
    else:
        conditions.append("價格範圍： 不指定")
    
    if chat_data["floormap"]:
        conditions.append("格局： {}".format(chat_data["floormap"]))
    else:
        conditions.append("格局： 不指定")

    update.message.reply_text("\n".join(conditions))
   

    # Crawle and Search
    kind = None if not chat_data["floormap"] else floormap_data[chat_data["floormap"]]
    mrtcoods = None if not chat_data["mrt_station"] else mrt_data[chat_data["mrtline"]][chat_data["mrt_station"]]
    crawler = HouseCrawler(kind=kind, 
                           mrtcoods=mrtcoods, 
                           from_price=chat_data["price_lower_bound"], 
                           to_price=chat_data["price_upper_bound"])
    res = crawler.find_page(0)
    if len(res) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text = "沒有符合條件的租屋物件")
    else:
        lines = ["總共有「{}」筆資料".format(len(res))]
        lines.append("更新時間：{}".format(res[0]["posttime"]))
        lines.append("價格：{}".format(res[0]["price"]))
        lines.append("類型：{}".format(res[0]["kind_name"]))
        lines.append("https://rent.591.com.tw/rent-detail-{}.html".format(res[0]["post_id"]))
        context.bot.send_message(chat_id=update.effective_chat.id, text = "\n".join(lines))

if __name__ == "__main__":
    # Load mrt station infomation
    _read_mrt()
    _read_floormap()

    bot_token = os.environ["bot_token"]
   
    updater = Updater(token=bot_token, use_context=True)

    dispatcher = updater.dispatcher
    
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    
    search_handler = CommandHandler('search', search)
    dispatcher.add_handler(search_handler)

    condition_handler = CommandHandler('condition', condition)
    dispatcher.add_handler(condition_handler)

    # Setting MRT
    # mrt_station_setting_handler = CommandHandler('mrt', mrt)
    # dispatcher.add_handler(mrt_station_setting_handler)
    # mrt_pattern = re.compile("|".join(list(mrt_data.keys())))
    # dispatcher.add_handler(CallbackQueryHandler(mrt_button, pattern=mrt_pattern))
    mrt_conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('mrt', mrt)],
            states={
                "MRTLINE": [CallbackQueryHandler(mrtline)],
                "MRTSTATION": [CallbackQueryHandler(mrt_station)]
                },
                fallbacks=[CommandHandler('mrt', mrt)]
            )
    dispatcher.add_handler(mrt_conversation_handler)
    
    # Setting Floormap
    floormap_setting_handler = CommandHandler('floormap', floormap)
    dispatcher.add_handler(floormap_setting_handler)
    floormap_pattern = re.compile("|".join(list(floormap_data.keys())))
    dispatcher.add_handler(CallbackQueryHandler(floormap_button, pattern=floormap_pattern))
    
    # Setting Price
    price_conversation_handler = ConversationHandler(
                                 entry_points=[CommandHandler('price', price)],
                                 states={
                                    "LOWER_PRICE": [CallbackQueryHandler(lower_price)],
                                    "UPPER_PRICE": [CallbackQueryHandler(upper_price)]
                                 },
                                 fallbacks=[CommandHandler('price', price)])
    dispatcher.add_handler(price_conversation_handler)
    # Setting Price
    # price_handler = CommandHandler('price', price)
    # dispatcher.add_handler(price_handler)
    # dispatcher.add_handler(CallbackQueryHandler(price_button))
    # echo_handler = MessageHandler(Filters.text, echo)
    # dispatcher.add_handler(echo_handler)
     
    updater.start_polling()

    updater.idle()


