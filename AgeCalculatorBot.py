#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from dateutil.relativedelta import relativedelta
from _datetime import datetime
import yaml
import time
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
    row.append([InlineKeyboardButton("Früher", callback_data=arg[0:1] + "prev" + ' ' + str(std_year)),
                InlineKeyboardButton("Später", callback_data=arg[0:1] + "next" + ' ' + str(std_year))])
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
    delete_date(chat_data, 's')
    delete_date(chat_data, 'g')
    update.message.reply_text(get_text(chat_data), reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


def navigate_year(update, chat_data, arg):
    new_year = int(update.callback_query.data.split(" ")[1])
    new_year = new_year + 12 if arg == "gnext" or arg == "snext" else new_year - 12
    update.callback_query.message.edit_text(get_text(chat_data),
                                            reply_markup=get_year_kb(4, 3, new_year, arg[0:1] + "year"),
                                            parse_mode=ParseMode.MARKDOWN)


def get_text(chat_data):
    result = "Geburtstag: *"
    result = result + str(chat_data["sday"]) + "." if "sday" in chat_data else result + "xx."
    result = result + str(chat_data["smonth"]) + "." if "smonth" in chat_data else result + "xx."
    result = result + str(chat_data["syear"]) + "*" if "syear" in chat_data else result + "xxxx*"
    result = result + "\nHeutiges Datum: *"
    result = result + str(chat_data["gday"]) + "." if "gday" in chat_data else result + "xx."
    result = result + str(chat_data["gmonth"]) + "." if "gmonth" in chat_data else result + "xx."
    result = result + str(chat_data["gyear"]) + "*" if "gyear" in chat_data else result + "xxxx*"
    return result


def get_goal_keyboard():
    keyboard = [[InlineKeyboardButton("Heute", callback_data="today")],
                [InlineKeyboardButton("Anderes Datum", callback_data="insert")]]
    return InlineKeyboardMarkup(keyboard)


def get_result_keyboard(exclude):
    keyboard = [[InlineKeyboardButton("Alter", callback_data="calc")],
                [InlineKeyboardButton("Absolutes Alter", callback_data="total")],
                [InlineKeyboardButton("Nächste Geburtstage", callback_data="next_birthdays")]]
    keyboard.pop(exclude)
    return InlineKeyboardMarkup(keyboard)


def get_calc_keyboard():
    keyboard = [[InlineKeyboardButton("Berechnen", callback_data="calc")],
                [InlineKeyboardButton("Korrigiere Geburtstag", callback_data="correct_start")],
                [InlineKeyboardButton("Korrigiere heutiges Datum", callback_data="correct_goal")]]
    return InlineKeyboardMarkup(keyboard)


def delete_date(chat_data, arg):
    chat_data.pop(arg + "year", None)
    chat_data.pop(arg + "month", None)
    chat_data.pop(arg + "day", None)


def time_since(chat_data):
    d1 = datetime.strptime(chat_data["sday"] + "." + chat_data["smonth"] + "." + chat_data["syear"], "%d.%m.%Y")
    d2 = datetime.strptime(chat_data["gday"] + "." + chat_data["gmonth"] + "." + chat_data["gyear"], "%d.%m.%Y")
    result = "*" + str(relativedelta(d2, d1).years) + "* Jahre\n"
    result = result + "*" + str(relativedelta(d2, d1).months) + "* Monate\n"
    result = result + "*" + str(relativedelta(d2, d1).days) + "* Tage\n"
    return result


def time_to(chat_data):
    d1 = datetime.strptime(chat_data["sday"] + "." + chat_data["smonth"] + "." + chat_data["gyear"], "%d.%m.%Y")
    d2 = datetime.strptime(chat_data["gday"] + "." + chat_data["gmonth"] + "." + chat_data["gyear"], "%d.%m.%Y")
    if d1 < d2:
        d1 = datetime.strptime(chat_data["sday"] + "." + chat_data["smonth"] + "." + str((int(chat_data["gyear"]) + 1)),
                               "%d.%m.%Y")
    result = "*" + str(relativedelta(d1, d2).months) + " *Monate\n"
    result = result + "*" + str(relativedelta(d1, d2).days) + "* Tage\n"
    return result


def total_time(chat_data):
    d1 = datetime.strptime(chat_data["sday"] + "." + chat_data["smonth"] + "." + chat_data["syear"], "%d.%m.%Y")
    d2 = datetime.strptime(chat_data["gday"] + "." + chat_data["gmonth"] + "." + chat_data["gyear"], "%d.%m.%Y")
    diff = d2 - d1
    days = diff.days
    seconds = diff.seconds

    result = "*" + str(int(days / 365.25)) + "* Jahre\n"
    result = result + "*" + str(int(days / 30.4375)) + "* Monate\n"
    result = result + "*" + str(int(days)) + "* Tage\n"
    result = result + "*" + str(int(days * 24 + seconds / 3600)) + "* Stunden\n"
    result = result + "*" + str(int(days * 24 * 60 + seconds / 60)) + "* Minuten\n"
    result = result + "*" + str(int(days * 24 * 3600 + seconds)) + "* Sekunden\n"
    return result


def weekdays(chat_data):
    days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    result = "Wochentage:\n"
    for i in range(10):
        result = result + chat_data["sday"] + "." + chat_data["smonth"] + "." + str(
            int(chat_data["gyear"]) + i) + ": *" + days[int(
            datetime.strptime(chat_data["sday"] + "." + chat_data["smonth"] + "." + str(int(chat_data["gyear"]) + i),
                              "%d.%m.%Y").weekday())] + "*\n"
    return result


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
        chat_data["gday"] = datetime.now().strftime("%d")
        chat_data["gmonth"] = datetime.now().strftime("%m")
        chat_data["gyear"] = datetime.now().strftime("%Y")
        update.callback_query.message.edit_text(get_text(chat_data), parse_mode=ParseMode.MARKDOWN,
                                                reply_markup=get_calc_keyboard())
    elif arg_one == "insert":
        keyboard = get_number_kb(8, 4, "gday", limit=31)
        update.callback_query.message.edit_text(get_text(chat_data), reply_markup=keyboard,
                                                parse_mode=ParseMode.MARKDOWN)
    elif arg_one == "correct_start" or arg_one == "correct_goal":
        delete_date(chat_data, arg_one.split("correct_")[1][0:1])
        keyboard = get_number_kb(8, 4, arg_one.split("correct_")[1][0:1] + "day", limit=31)
        update.callback_query.message.edit_text(get_text(chat_data), reply_markup=keyboard,
                                                parse_mode=ParseMode.MARKDOWN)
    elif arg_one == "calc":
        try:
            text = "Alter:\n" + time_since(chat_data) + "\nNächster Geburtstag:\n" + time_to(chat_data)
            update.callback_query.message.edit_text(get_text(chat_data) + "\n\n" + text, parse_mode=ParseMode.MARKDOWN,
                                                    reply_markup=get_result_keyboard(0))
        except ValueError:
            update.callback_query.message.reply_text("Achtung, ungültiges Datum...\nVersuche es bitte erneut")
            start(bot, update.callback_query, chat_data)
    elif arg_one == "total":
        text = "Total:\n" + total_time(chat_data)
        update.callback_query.message.edit_text(get_text(chat_data) + "\n\n" + text, parse_mode=ParseMode.MARKDOWN,
                                                reply_markup=get_result_keyboard(1))
    elif arg_one == "next_birthdays":
        text = weekdays(chat_data)
        update.callback_query.message.edit_text(get_text(chat_data) + "\n\n" + text, parse_mode=ParseMode.MARKDOWN,
                                                reply_markup=get_result_keyboard(2))


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
