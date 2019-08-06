#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from dateutil.relativedelta import relativedelta
from _datetime import datetime, timedelta



# Set dictionary with strings
def set_strings(the_strings):
    global strings
    strings = the_strings


# Set today in chat data
def set_today(chat_data):
    chat_data["gday"] = datetime.now().strftime("%d")
    chat_data["gmonth"] = datetime.now().strftime("%m")
    chat_data["gyear"] = datetime.now().strftime("%Y")

# Calculates years, months and days from birthday until today
def __time_since(chat_data):
    d1 = datetime.strptime(chat_data["sday"] + "." + chat_data["smonth"] + "." + chat_data["syear"], "%d.%m.%Y")
    d2 = datetime.strptime(chat_data["gday"] + "." + chat_data["gmonth"] + "." + chat_data["gyear"], "%d.%m.%Y")
    result = "*" + str(relativedelta(d2, d1).years) + "* " + strings[chat_data["lang"]]["years"] + "\n"
    result = result + "*" + str(relativedelta(d2, d1).months) + "* " + strings[chat_data["lang"]]["months"] + "\n"
    result = result + "*" + str(relativedelta(d2, d1).days) + "* " + strings[chat_data["lang"]]["days"] + "\n"
    return result


# Calculates years, months and days from today until next birthday
def __time_to(chat_data):
    d1 = datetime.strptime(chat_data["sday"] + "." + chat_data["smonth"] + "." + chat_data["gyear"], "%d.%m.%Y")
    d2 = datetime.strptime(chat_data["gday"] + "." + chat_data["gmonth"] + "." + chat_data["gyear"], "%d.%m.%Y")
    if d1 < d2:
        d1 = datetime.strptime(chat_data["sday"] + "." + chat_data["smonth"] + "." + str((int(chat_data["gyear"]) + 1)),
                               "%d.%m.%Y")
    result = "*" + str(relativedelta(d1, d2).months) + "* " + strings[chat_data["lang"]]["months"] + "\n"
    result = result + "*" + str(relativedelta(d1, d2).days) + "* " + strings[chat_data["lang"]]["days"] + "\n"
    return result


# Get birthday and today from chat data
def get_dates(chat_data):
    time = chat_data["bhour"] + ":" + chat_data["bmin"] if "bhour" in chat_data else "00:00"
    bday = datetime.strptime(
        chat_data["sday"] + "." + chat_data["smonth"] + "." + chat_data["syear"] + " " + time, "%d.%m.%Y %H:%M")
    tday = datetime.strptime(
        chat_data["gday"] + "." + chat_data["gmonth"] + "." + chat_data["gyear"] + " " + datetime.now().strftime(
            "%H:%M:%S"), "%d.%m.%Y %H:%M:%S")
    return bday, tday


# Calculate age in years, months, days, hours, minutes and seconds
def total_time(chat_data):
    bday, tday = get_dates(chat_data)
    diff = tday - bday
    days = diff.days
    seconds = diff.seconds
    relative = relativedelta(tday, bday)

    result = "*" + str('{0:,}'.format(int(days / 365.25))) + "* " + strings[chat_data["lang"]]["years"] + "\n"
    result = result + "*" + str('{0:,}'.format((relative.years * 12 + relative.months))) + "* " + strings[chat_data["lang"]][
        "months"] + "\n"
    result = result + "*" + str('{0:,}'.format(int(days))) + "* " + strings[chat_data["lang"]]["days"] + "\n"
    result = result + "*" + str('{0:,}'.format(int(days * 24 + seconds / 3600))) + "* " + strings[chat_data["lang"]][
        "hours"] + "\n"
    result = result + "*" + str('{0:,}'.format(int(days * 24 * 60 + seconds / 60))) + "* " + strings[chat_data["lang"]][
        "minutes"] + "\n"
    result = result + "*" + str('{0:,}'.format(int(days * 24 * 3600 + seconds))) + "* " + strings[chat_data["lang"]][
        "seconds"] + "\n"
    if strings[chat_data['lang']]['seperator'] == "dot":
        result = result.replace(',', '.')
    return result


# Calculates upcoming month events
def __special_month(bday, d_age, chat_data, add=0, repdigit=False):
    number = __next_big(d_age / 30.4375, add=add) if not repdigit else __calculate_repdigit(int(d_age / 30.4375))
    month = strings[chat_data["lang"]]["month_list"].split(", ")
    next = number * int(math.ceil((d_age / 30.4375) / number))
    next_d = bday + timedelta(days=next * 30.4375)
    result = '\n\n*' + str('{0:,}'.format(next)) + ' ' + strings[chat_data["lang"]]["months"] + ':\n*' + str(
        month[next_d.date().month - 1]) + '. ' + str(next_d.date().year)
    if strings[chat_data['lang']]['seperator'] == "dot":
        result = result.replace(',', '.')
    return result, next_d


# Calculates upcoming day events
def __special_days(bday, d_age, chat_data, add=0, repdigit=False):
    number = __next_big(d_age, add=add) if not repdigit else __calculate_repdigit(int(d_age))
    next = number * int(math.ceil(d_age / number))
    next_d = bday + timedelta(days=next)
    result = '\n\n*' + str('{0:,}'.format(next)) + ' ' + strings[chat_data["lang"]][
        "days"] + ':\n*' + datetime.strftime(
        next_d, "%d.%m.%Y")
    if strings[chat_data['lang']]['seperator'] == "dot":
        result = result.replace(',', '.')
    return result, next_d


# Calculates upcoming hour events
def __special_hours(bday, s_age, chat_data, add=0, repdigit=False):
    number = __next_big(s_age / 3600, add=add) if not repdigit else __calculate_repdigit(int(s_age / 3600))
    next = number * int(math.ceil((s_age / 3600) / number))
    next_d = bday + timedelta(hours=next)
    result = '\n\n*' + str('{0:,}'.format(next)) + ' ' + strings[chat_data["lang"]][
        "hours"] + ':\n*' + datetime.strftime(
        next_d, "%d.%m.%Y %H:%M")
    if strings[chat_data['lang']]['seperator'] == "dot":
        result = result.replace(',', '.')
    return result, next_d


# Calculates upcoming minute events
def __special_minutes(bday, s_age, chat_data, add=0, repdigit=False):
    number = __next_big(s_age / 60, add=add) if not repdigit else __calculate_repdigit(int(s_age / 60))
    next = number * int(math.ceil((s_age / 60) / number))
    next_d = bday + timedelta(minutes=next)
    result = '\n\n*' + str('{0:,}'.format(next)) + ' ' + strings[chat_data["lang"]][
        "minutes"] + ':\n*' + datetime.strftime(next_d, "%d.%m.%Y %H:%M")
    if strings[chat_data['lang']]['seperator'] == "dot":
        result = result.replace(',', '.')
    return result, next_d


# Calculates upcoming second events
def __special_seconds(bday, s_age, chat_data, add=0, repdigit=False):
    number = __next_big(s_age, add=add) if not repdigit else __calculate_repdigit(int(s_age))
    next = number * int(math.ceil(s_age / number))
    next_d = bday + timedelta(seconds=next)
    result = '\n\n*' + str('{0:,}'.format(next)) + ' ' + strings[chat_data["lang"]][
        "seconds"] + ':\n*' + datetime.strftime(next_d, "%d.%m.%Y %H:%M:%S")
    if strings[chat_data['lang']]['seperator'] == "dot":
        result = result.replace(',', '.')
    return result, next_d


# Check if repdigit must bigger or smaller than first digit
def __next_repdigit(number):
    for i in range(len(str(number))):
        if str(number)[i:i + 1] > str(number)[:1]:
            return False
        elif str(number)[i:i + 1] < str(number)[:1]:
            return True
    return True


# Calculate the next number with repeated digits
def __calculate_repdigit(number):
    if __next_repdigit(number):
        result = int(str(number)[:1] * len(str(number)))
    else:
        result = int(str(int(str(number)[:1]) + 1) * len(str(number)))
    return result


# Calculates the next round number
def __next_big(number, add=0):
    result = math.ceil(number / int(str('1' + '0' * int(len(str(int(number))) - add))))
    result = result * int(str('1' + '0' * int(len(str(int(number))) - add)))
    return result


# Catch ZeroDivisonError at calculating special events and show error message
def calculate_special_events(chat_data):
    try:
        return __special_events(chat_data)
    except ZeroDivisionError:
        return "\n‼️‼️‼️\n" + strings[chat_data['lang']]['events_error'] + "\n‼️‼️‼️"


# Calculate list with special dates
def __calulate_date_list(chat_data):
    bday, tday = get_dates(chat_data)
    d_age = (tday - bday).days
    s_age = (tday - bday).total_seconds()

    date_list = []
    date_list.append(__special_month(bday, d_age, chat_data, add=1))
    date_list.append(__special_month(bday, d_age, chat_data, add=2))
    date_list.append(__special_month(bday, d_age, chat_data, repdigit=True))
    date_list.append(__special_days(bday, d_age, chat_data, add=1))
    date_list.append(__special_days(bday, d_age, chat_data, add=2))
    date_list.append(__special_days(bday, d_age, chat_data, repdigit=True))
    date_list.append(__special_hours(bday, s_age, chat_data, add=1))
    date_list.append(__special_hours(bday, s_age, chat_data, add=2))
    date_list.append(__special_hours(bday, s_age, chat_data, repdigit=True))
    date_list.append(__special_minutes(bday, s_age, chat_data, add=1))
    date_list.append(__special_minutes(bday, s_age, chat_data, add=2))
    date_list.append(__special_minutes(bday, s_age, chat_data, repdigit=True))
    date_list.append(__special_seconds(bday, s_age, chat_data, add=1))
    date_list.append(__special_seconds(bday, s_age, chat_data, add=2))
    date_list.append(__special_seconds(bday, s_age, chat_data, repdigit=True))
    return date_list


# Get string with special dates
def __special_events(chat_data):
    date_list = __calulate_date_list(chat_data)
    date_list = list(set(date_list))
    date_list = sorted(date_list, key=lambda x: x[1])
    result = [x[0] for x in date_list]
    return str(''.join(result))


# Get string with time until birth and time until next
def calculate(chat_data):
    result = strings[chat_data["lang"]]["age"] + ":\n" + __time_since(chat_data) + "\n" + \
             strings[chat_data["lang"]]["upcoming"] + ":\n" + __time_to(chat_data)
    return result


# Calculate weekday of birth and weekdays of the next ten birthday
def weekdays(chat_data):
    d1 = datetime.strptime(chat_data["sday"] + "." + chat_data["smonth"] + "." + chat_data["gyear"], "%d.%m.%Y")
    d2 = datetime.strptime(chat_data["gday"] + "." + chat_data["gmonth"] + "." + chat_data["gyear"], "%d.%m.%Y")
    add = 1 if d1 < d2 else 0
    days = strings[chat_data["lang"]]["days_list"].split(", ")
    birthday = chat_data["sday"] + "." + chat_data["smonth"] + "." + chat_data["syear"]
    birth_weekday = days[
        int(datetime.strptime(chat_data["sday"] + "." + chat_data["smonth"] + "." + chat_data["syear"],
                              "%d.%m.%Y").weekday())]
    result = strings[chat_data["lang"]]["weekdays"] + ':\n' + birthday + ': *' + birth_weekday \
             + "*\n----------------------------------------\n"
    for i in range(10):
        result = result + chat_data["sday"] + "." + chat_data["smonth"] + "." + str(
            int(chat_data["gyear"]) + i + add) + ": *" + days[int(
            datetime.strptime(
                chat_data["sday"] + "." + chat_data["smonth"] + "." + str(int(chat_data["gyear"]) + i + add),
                "%d.%m.%Y").weekday())] + "*\n"
    return result
