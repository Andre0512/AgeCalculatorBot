#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import yaml
from telegram import ReplyKeyboardMarkup, KeyboardButton, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def get_yml(file):
    with open(os.path.join(os.path.dirname(__file__), file), 'rb') as ymlfile:
        result = yaml.load(ymlfile)
    return result


def get_number_kb(c, r, callback, limit=99, name_list=()):
    row = []
    for i in range(r):
        column = []
        for j in range(c):
            pos = str(i * c + (j + 1))
            full_name = "0" + pos if int(pos) < 10 else pos
            name = full_name if not name_list else name_list[int(pos) - 1]
            if int(pos) < limit + 1:
                column.append(InlineKeyboardButton(name, callback_data=callback + ' ' + full_name))
        row.append(column)
    return InlineKeyboardMarkup(row)


def start(bot, update):
    keyboard = get_number_kb(8, 4, "day", limit=31)
    month = ('Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez')
    # month = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    #keyboard = get_number_kb(3, 4, "month", name_list=month)
    update.message.reply_text('Startdatum: xx.xx.xxxx', reply_markup=keyboard)

def button(bot, update, chat_data):
    update.callback_query.answer()
    if update.callback_query.data.split(" ")[0] == "day":
        chat_data["day"] = update.callback_query.data.split(" ")[1]
        month = ('Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez')
        reply_text = 'Startdatum: ' + str(chat_data["day"]) + '.xx.xxxx'
        update.callback_query.message.edit_text(reply_text, reply_markup=get_number_kb(3, 4, "month", name_list=month))
    elif update.callback_query.data.split(" ")[0] == "month":
        chat_data["day"] = update.callback_query.data.split(" ")[1]

def main():
    updater = Updater(get_yml('./config.yml')['agecalculator']['bottoken'])

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text, start))
    dp.add_handler(CallbackQueryHandler(button, pass_chat_data=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
