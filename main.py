import datetime

import telebot
from telebot import types

import dbHandler
from yamlHandler import YamlHandler
from dbHandler import SqliteDB

# ---------------VARIABLES---------------

ShnapBot = ""
BsaverBot = ""

bot_data = {
    "bot": {
        "API_KEY": "5187477632:AAHw_HitQ4jw1SQqGvpQ0VULXpB9D9WkbrQ",
        "USERNAME": "BsaverBot",
        "ID": 0
    }
}

responses_data = {
    "responses": {
        "ADD_COMMAND": """Who would you like to add?

*You can type multiple entries*

Format : 
    firstname lastname dd/mm
""",
        "ADD_SUCCESS": "Added users",
        "ADD_ERROR": "Couldn't add user.\nReason:\n",
        "HELP": """""",
        "REMOVE_COMMAND": """Who would you like to remove?

*You can type multiple entries*

Format : 
    firstname lastname
""",
        "REMOVE_ERROR": "Couldn't remove user.\nReason:\n",

    }
}

# markup = types.InlineKeyboardMarkup()
# markup.row_width = 2
# markup.add(types.InlineKeyboardButton("Yes", callback_data="/start"),
#            types.InlineKeyboardButton("No", callback_data="start"))

replyMarkup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
replyMarkup.add('/add', '/remove','/when','/close','/today','/help')

ADD_TEXT = """Who would you like to add?

*You can type multiple entries*

Format : 
    firstname lastname dd/mm
"""

#########################################





if __name__ == '__main__':
    data = YamlHandler.yaml_loader("config.yaml")
    botData = data["bot"]
    # bot_data.update(responses_data)
    # YamlHandler.yaml_dump("config.yaml", bot_data)
    responses = data["responses"]

    bot = telebot.TeleBot(botData["API_KEY"])
    db = dbHandler.SqliteDB("userDB.db")
    # db.create_userTable()


#
@bot.message_handler(commands=['start', "help"])
def start(message):
    msg = bot.send_message(message.chat.id, responses['START_COMMAND'], reply_markup=replyMarkup,parse_mode='HTML')
    # bot.register_next_step_handler(msg,start)
    print(message)


###################################################################
@bot.message_handler(commands=['add'])
def add(message):
    msg = bot.send_message(message.chat.id, text=responses["ADD_COMMAND"])
    bot.register_next_step_handler(msg, add_process)


def add_process(message):
    outcome = add_users(message)

    if outcome:
        msg = bot.send_message(message.chat.id, text=responses["ADD_SUCCESS"], reply_markup=replyMarkup)


def add_users(message):
    for value, userRecord in enumerate(message.text.split('\n')):
        userRecordSplitted = removeEmptyVal(userRecord)
        outcome = validateLen(userRecordSplitted, 3)

        if not outcome:
            error_call("ADD", f"Line {value + 1} \n Need 3 values, got {len(userRecordSplitted)}", message.chat.id)
            continue

        first, last, date = userRecordSplitted[0], userRecordSplitted[1], userRecordSplitted[2]
        if validateName(first) and validateName(last) and validateDate(date):
            db.insert_user(first, last, date)

        else:
            print("validation error")
            error_call("ADD", f"Line {value + 1} \n Syntax is wrong", message.chat.id)
    return True


#######################################################################


@bot.message_handler(commands=['delete', 'remove'])
def remove(message):
    msg = bot.send_message(message.chat.id, text=responses["REMOVE_COMMAND"])
    bot.register_next_step_handler(msg, remove_process)


def remove_process(message):
    outcome = remove_users(message)

    if outcome:
        msg = bot.send_message(message.chat.id, text=responses["REMOVE_SUCCESS"], reply_markup=replyMarkup)


def remove_users(message):
    for value, userRecord in enumerate(message.text.split('\n')):
        userRecordSplitted = removeEmptyVal(userRecord)
        outcome = validateLen(userRecordSplitted, 2)

        if not outcome:
            error_call("REMOVE", f"Line {value + 1} \n Need 2 values, got {len(userRecordSplitted)}", message.chat.id)
            continue

        first, last = userRecordSplitted[0], userRecordSplitted[1]
        if validateName(first) and validateName(last):
            outcome = db.delete(first, last)

            if not outcome:
                error_call("REMOVE", f"Line {value + 1} \n User doesn't exist", message.chat.id)
                continue

        else:
            print("validation error")
            error_call("REMOVE", f"Line {value + 1} \n Wrong Syntax", message.chat.id)
            continue
    return True


#############################################################


@bot.message_handler(commands=["when"])
def when(message):
    msg = bot.send_message(message.chat.id, text=responses["WHEN_COMMAND"])
    bot.register_next_step_handler(msg, when_process)


def when_process(message):
    userRecord = message.text.replace("*", "%")
    userRecordSplitted = removeEmptyVal(userRecord)
    first = userRecordSplitted[0]
    last = "%"
    if len(userRecordSplitted) > 2:
        error_call("WHEN", f"Need at most 2 values, got {len(userRecordSplitted)}", message.chat.id)

    elif len(userRecordSplitted) == 2:
        last = userRecordSplitted[1]

    if validateName(first.replace("%", "")) and validateName(last.replace("%", "")):
        users = db.likeSearch(first, last)
        if len(users) == 0:
            error_call("WHEN", f"User doesn't exist", message.chat.id)
        else:
            print(users[0][3])
            print(type(users[0][3]))
            users.sort(key=lambda user: datetime.datetime.strptime(f'{user[3]}', "%d/%m"))
            bot.send_message(message.chat.id, text=f"{responses['WHEN_SUCCESS']} {convertListToString(users)}", reply_markup=replyMarkup)
    else:
        print("validation error")
        error_call("WHEN", "Wrong Syntax", message.chat.id)


######################



@bot.message_handler(commands=['close'])
def close(message):
    msg = bot.send_message(message.chat.id, text=responses["CLOSE_COMMAND"])
    bot.register_next_step_handler(msg, close_process)


def close_process(message):
    if not message.text.isdigit():
        error_call("CLOSE", "Wrong Syntax", message.chat.id)
        return

    userInput = int(message.text)

    if userInput > 365:
        error_call("CLOSE", "Input exceeding available range", message.chat.id)
        return

    currentDate = datetime.date.today()
    endDate = currentDate + datetime.timedelta(days=userInput)
    users = db.likeSearch("%")
    closeDates = []
    for user in users:
        userDate = datetime.datetime.strptime(f'{user[3]}', "%d/%m").date()
        userDate = userDate.replace(year=currentDate.year)
        if currentDate <= userDate <= endDate:
            closeDates.append(user)

    if len(closeDates) == 0:
        bot.send_message(message.chat.id, text="Couldn't find any users in the specified date range", reply_markup=replyMarkup)

    else:
        closeDates.sort(key=lambda user: datetime.datetime.strptime(f'{user[3]}', "%d/%m"))
        bot.send_message(message.chat.id, text=f"{responses['WHEN_SUCCESS']} {convertListToString(closeDates)}", reply_markup=replyMarkup)




#####################################

@bot.message_handler(commands=["today"])
def today(message):
    message.text = "0"
    close_process(message)

##########################

# @bot.message_handler(commands=["test"])
# def test(message):
#     print(message.text.split(" "))
#     print(db.search(message.text.split(" ")[1], message.text.split(" ")[2]))


######################

def validateLen(userRecordSplitted, parameters):
    print(userRecordSplitted)
    if len(userRecordSplitted) < parameters:
        print("len error")
        return False
    return True


def validateName(name):
    return name.isalpha() or name == ""


def validateDate(date):
    print(date)
    dateSplitted = date.split("/")
    if len(dateSplitted) != 2:
        return False
    day, month = dateSplitted
    try:
        datetime.date(day=int(day), month=int(month), year=2000)
        return True
    except ValueError:
        return False


def removeEmptyVal(text):
    textSplitted = text.split(" ")
    without_empty_strings = []
    for string in textSplitted:
        if string != "":
            without_empty_strings.append(string)
    return without_empty_strings


def convertListToString(array):
    text = ""
    for innerTuple in array:
        innerArray = list(innerTuple)
        del innerArray[0]
        text += " ".join(innerArray) + "\n"
    return text


def error_call(command, reason, chatID):
    bot.send_message(chatID, text=f'{responses[f"{command}_ERROR"]} {reason}', reply_markup=replyMarkup)


bot.polling()
