#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging

import datetime
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


def get_year_kb(c, r, year, arg):
    row = []
    std_year = year
    for i in range(r):
        column = []
        for j in range(c):
            column.append(InlineKeyboardButton(str(year), callback_data=arg + ' ' + str(year)))
            year = 1 + year
        row.append(column)
    row.append([InlineKeyboardButton("Previous", callback_data=arg[0:1] + "prev" + ' ' + str(std_year)),
                InlineKeyboardButton("Next", callback_data=arg[0:1] + "next" + ' ' + str(std_year))])
    return InlineKeyboardMarkup(row)


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


def start(bot, update, chat_data):
    keyboard = get_number_kb(8, 4, "sday", limit=31)
    month = ('Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez')
    # month = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    # keyboard = get_number_kb(3, 4, "month", name_list=month)
    update.message.reply_text(get_text(chat_data), reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


def navigate_year(update, chat_data, arg):
    new_year = int(update.callback_query.data.split(" ")[1])
    new_year = new_year + 12 if arg == "gnext" or arg == "snext" else new_year - 12
    update.callback_query.message.edit_text(get_text(chat_data),
                                            reply_markup=get_year_kb(4, 3, new_year, arg[0:1] + "year"),
                                            parse_mode=ParseMode.MARKDOWN)


def get_text(chat_data):
    result = "Startdatum: *"
    result = result + str(chat_data["sday"]) + "." if "sday" in chat_data else result + "xx."
    result = result + str(chat_data["smonth"]) + "." if "smonth" in chat_data else result + "xx."
    result = result + str(chat_data["syear"]) + "*" if "syear" in chat_data else result + "xxxx*"
    result = result + "\nZieldatum: *"
    result = result + str(chat_data["gday"]) + "." if "gday" in chat_data else result + "xx."
    result = result + str(chat_data["gmonth"]) + "." if "gmonth" in chat_data else result + "xx."
    result = result + str(chat_data["gyear"]) + "*" if "gyear" in chat_data else result + "xxxx*"
    return result


def get_goal_keyboard():
    keyboard = [[InlineKeyboardButton("Today", callback_data="today")],
                [InlineKeyboardButton("Insert date", callback_data="insert")]]
    return InlineKeyboardMarkup(keyboard)


def get_calc_keyboard():
    keyboard = [[InlineKeyboardButton("Berechne", callback_data="calc")],
                [InlineKeyboardButton("Korrigiere Startdatum", callback_data="correct_start")],
                [InlineKeyboardButton("Korrigiere Zieldatum", callback_data="correct_goal")]]
    return InlineKeyboardMarkup(keyboard)


def delete_date(chat_data, arg):
    chat_data.pop(arg + "year", None)
    chat_data.pop(arg + "month", None)
    chat_data.pop(arg + "day", None)


def button(bot, update, chat_data):
    update.callback_query.answer()
    arg_one = update.callback_query.data.split(" ")[0]
    if arg_one == "sday" or arg_one == "gday":
        chat_data[arg_one] = update.callback_query.data.split(" ")[1]
        month = ('Jan', 'Feb', 'Mrz', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez')
        update.callback_query.message.edit_text(get_text(chat_data),
                                                reply_markup=get_number_kb(3, 4, arg_one[0:1] + "month",
                                                                           name_list=month),
                                                parse_mode=ParseMode.MARKDOWN)
    elif arg_one == "smonth" or arg_one == "gmonth":
        chat_data[arg_one] = update.callback_query.data.split(" ")[1]
        update.callback_query.message.edit_text(get_text(chat_data),
                                                reply_markup=get_year_kb(4, 3, 1980, arg_one[0:1] + "year"),
                                                parse_mode=ParseMode.MARKDOWN)
    elif arg_one == "syear" or arg_one == "gyear":
        chat_data[arg_one] = update.callback_query.data.split(" ")[1]
        keyboard = get_calc_keyboard() if "syear" in chat_data and "gyear" in chat_data else get_goal_keyboard()
        update.callback_query.message.edit_text(get_text(chat_data), reply_markup=keyboard,
                                                parse_mode=ParseMode.MARKDOWN)
    elif arg_one == "snext" or arg_one == "sprev" or arg_one == "gnext" or arg_one == "gprev":
        navigate_year(update, chat_data, arg_one)
    elif arg_one == "today":
        chat_data["gday"] = datetime.datetime.now().strftime("%d")
        chat_data["gmonth"] = datetime.datetime.now().strftime("%m")
        chat_data["gyear"] = datetime.datetime.now().strftime("%Y")
        update.callback_query.message.edit_text(get_text(chat_data), parse_mode=ParseMode.MARKDOWN,
                                                reply_markup=get_calc_keyboard())
    elif arg_one == "insert":
        keyboard = get_number_kb(8, 4, "gday", limit=31)
        update.callback_query.message.edit_text(get_text(chat_data), reply_markup=keyboard,
                                                parse_mode=ParseMode.MARKDOWN)
    elif arg_one == "correct_start" or arg_one == "correct_goal":
        keyboard = get_number_kb(8, 4, arg_one.split("correct_")[1][0:1] + "day", limit=31)
        delete_date(chat_data, arg_one.split("correct_")[1][0:1])
        update.callback_query.message.edit_text(get_text(chat_data), reply_markup=keyboard,
                                                parse_mode=ParseMode.MARKDOWN)


def main():
    updater = Updater(get_yml('./config.yml')['agecalculator']['bottoken'])

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start, pass_chat_data=True))
    dp.add_handler(MessageHandler(Filters.text, start, pass_chat_data=True))
    dp.add_handler(CallbackQueryHandler(button, pass_chat_data=True))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
