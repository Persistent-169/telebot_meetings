import telebot
import shelve
import time
import os

"""from boto.s3.connection import S3Connection

TG_TOKEN = os.getenv('TG_TOKEN')
"""
bot = telebot.TeleBot("1171659684:AAGr4vOnru6xxl7pYQO-5MxuLvsWSb_zqs8")


@bot.message_handler(commands=['start'])
def start(message):
    with shelve.open('info', writeback=True) as info:
        ID = str(message.chat.id)
        if ID in info.keys() and info[ID]["other_id"]:
            info[info[ID]["other_id"]]["other_id"] = ""
        info[ID] = {"action": "0",
                    "my_profile": {"gender": "", "age": "", "info": ""},
                    "find": {"gender": '', "age_from": '', "age_to": ''},
                    "other_id": '',
                    "black_list": [],
                    "signal": '0',
                    "request_answer": "unknown",
                    "my_time": {"time": "", "flag": "0"}}
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text='Женский', callback_data='Женский my_gender'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Мужской', callback_data='Мужской my_gender'))
        bot.delete_message(ID, message.message_id)
        bot.send_message(chat_id=ID, text='Заполняем вашу анкету.\nВыберите ваш пол: ', reply_markup=keyboard)


@bot.message_handler(commands=['my_profile'])
def my_profile(message):
    ID = str(message.chat.id)
    with shelve.open('info') as info:
        print(info[ID])
        bot.delete_message(ID, message.message_id)
        bot.send_message(chat_id=ID, text="_разит_", parse_mode="Markdown")


@bot.message_handler(commands=['who_i_need'])
def who(message):
    ID = str(message.chat.id)
    with shelve.open('info', writeback=True) as info:
        info[ID]["action"] = "3"
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text='Женский', callback_data='Женский find_gender'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Мужской', callback_data='Мужской find_gender'))
        keyboard.add(
            telebot.types.InlineKeyboardButton(text='Не имеет значения', callback_data='Женский Мужской find_gender'))
        bot.delete_message(chat_id=ID, message_id=message.message_id)
        bot.send_message(chat_id=ID, text='Выберите желаемый пол:', reply_markup=keyboard)


@bot.message_handler(commands=['leave_chat'])
def leave_chat(message):
    ID = str(message.chat.id)
    with shelve.open('info', writeback=True) as info:
        if info[ID]["other_id"]:
            bot.send_message(chat_id=ID, text="Вы вышли из чата. Нажмите /search, чтобы найти нового собеседника.")
            bot.send_message(chat_id=info[ID]["other_id"],
                             text="Ваш собеседник вышел из чата. Нажмите /search, чтобы найти нового собеседника.")
            info[ID]['black_list'] = info[ID]["black_list"] + [info[ID]["other_id"]]
            info[info[ID]["other_id"]]["other_id"] = ""
            info[ID]['other_id'] = ''
            bot.delete_message(ID, message.message_id)


def my_profile_gender(info_id, gender, ID, message_id, keyboard):
    info_id["my_profile"]["gender"] = gender
    bot.delete_message(chat_id=ID, message_id=message_id)
    bot.send_message(chat_id=ID, text='Укажите ваш возраст: ', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'my_gender' in call.data)
def gender(call):
    with shelve.open('info', writeback=True) as info:
        ID = str(call.message.chat.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for x in range(6, 61, 6):
            keyboard.row(telebot.types.InlineKeyboardButton(text=str(x), callback_data=str(x) + 'my_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 1), callback_data=str(x + 1) + 'my_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 2), callback_data=str(x + 2) + 'my_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 3), callback_data=str(x + 3) + 'my_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 4), callback_data=str(x + 4) + 'my_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 5), callback_data=str(x + 5) + 'my_age')
                         )
        keyboard.add(telebot.types.InlineKeyboardButton(text="Другой возраст (указать самостоятельно)",
                                                        callback_data="dif_age my_age"))
        my_profile_gender(info[ID], call.data[:call.data.find('m') - 1], ID, call.message.message_id, keyboard)


def my_profile_age(info_id, age, ID, message_id):
    bot.delete_message(chat_id=ID, message_id=message_id)
    if age == "dif_age ":
        info_id["action"] = '1'
        bot.send_message(chat_id=ID, text="Введите ваш возраст: ")
    else:
        info_id["my_profile"]["age"] = age
        info_id["action"] = '2'
        bot.send_message(chat_id=ID, text='Расскажите о себе: ')


@bot.callback_query_handler(func=lambda call: 'my_age' in call.data)
def age(call):
    with shelve.open('info', writeback=True) as info:
        ID = str(call.message.chat.id)
        my_profile_age(info[ID], call.data[:call.data.find('m')], ID, call.message.message_id)


def find_gender_act(info_id, gender, ID, message_id, keyboard):
    info_id["find"]["gender"] = gender
    bot.delete_message(chat_id=ID, message_id=message_id)
    bot.send_message(chat_id=ID, text="Укажите нижнюю возрастную границу: ", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'find_gender' in call.data)
def find_gender(call):
    with shelve.open('info', writeback=True) as info:
        ID = str(call.message.chat.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for x in range(6, 61, 6):
            keyboard.row(telebot.types.InlineKeyboardButton(text=str(x), callback_data=str(x) + 'find_from_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 1),
                                                            callback_data=str(x + 1) + 'find_from_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 2),
                                                            callback_data=str(x + 2) + 'find_from_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 3),
                                                            callback_data=str(x + 3) + 'find_from_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 4),
                                                            callback_data=str(x + 4) + 'find_from_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 5), callback_data=str(x + 5) + 'find_from_age')
                         )
        keyboard.add(telebot.types.InlineKeyboardButton(text="Другой возраст (указать самостоятельно)",
                                                        callback_data="d_age find_from_age"))
        find_gender_act(info[ID], call.data[:call.data.find('f') - 1], ID, call.message.message_id, keyboard)


def find_from_age_act(info_id, from_age, ID, message_id, keyboard):
    bot.delete_message(chat_id=ID, message_id=message_id)
    if from_age == "d_age ":
        info_id["action"] = "3"
        bot.send_message(chat_id=ID, text="Введите нижнюю возрастную границу: ")
    else:
        info_id["find"]["age_from"] = from_age
        bot.send_message(chat_id=ID, text='Укажите верхнюю возрастную границу: ', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'find_from_age' in call.data)
def find_from_age(call):
    with shelve.open('info', writeback=True) as info:
        ID = str(call.message.chat.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for x in range(6, 61, 6):
            keyboard.row(telebot.types.InlineKeyboardButton(text=str(x), callback_data=str(x) + 'find_to_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 1), callback_data=str(x + 1) + 'find_to_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 2), callback_data=str(x + 2) + 'find_to_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 3), callback_data=str(x + 3) + 'find_to_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 4), callback_data=str(x + 4) + 'find_to_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 5), callback_data=str(x + 5) + 'find_to_age')
                         )
        keyboard.add(telebot.types.InlineKeyboardButton(text="Другой возраст (указать самостоятельно)",
                                                        callback_data="d_age find_to_age"))
        find_from_age_act(info[ID], call.data[:call.data.find('f')], ID, call.message.message_id, keyboard)


def find_to_age_act(info_id, to_age, ID, message_id):
    bot.delete_message(chat_id=ID, message_id=message_id)
    if to_age == "d_age ":
        info_id["action"] = "4"
        bot.send_message(chat_id=ID, text="Введите верхнюю возрастную границу: ")
    else:
        info_id["find"]["age_to"] = to_age
        bot.send_message(chat_id=ID, text='Информация сохранена.')
        bot.send_message(chat_id=ID, text="Нажмите /search, чтобы начать поиск подходящего собеседника.")


@bot.callback_query_handler(func=lambda call: 'find_to_age' in call.data)
def find_to_age(call):
    with shelve.open('info', writeback=True) as info:
        ID = str(call.message.chat.id)
        find_to_age_act(info[ID], call.data[:call.data.find('f')], ID, call.message.message_id)


def consent_to_connect_act(info_id, info_key, ID, key, message_id, answer):
    bot.delete_message(chat_id=ID, message_id=message_id)
    info_id["request_answer"] = answer[0]
    if info_id['request_answer'] == 'yes':
        if info_key['request_answer'] == 'no':
            bot.send_message(chat_id=ID, text='Пользователь отказал в соединении.')
            info_id["request_answer"] = "unknown"
            info_key["request_answer"] = "unknown"
        elif info_key['request_answer'] == 'yes':
            info_key["other_id"] = ID
            info_key["signal"] = "0"
            info_key["request_answer"] = "unknown"
            info_id["other_id"] = key
            info_id["signal"] = "0"
            info_id["request_answer"] = "unknown"
            bot.send_message(chat_id=ID, text='Соединение установлено.')
            bot.send_message(chat_id=key, text='Соединение установлено.')
            info_id['my_time']["time"] = str(time.time())
            info_id["my_time"]["flag"] = "0"
            info_key['my_time']["time"] = str(time.time())
            info_key["my_time"]["flag"] = "0"
        elif info_key['request_answer'] == 'unknown':
            bot.send_message(chat_id=ID, text='Пользователь еще не дал ответ. Пожалуйста, подождите.')
    else:
        info_id["signal"] = "0"
        info_key["signal"] = "0"
        bot.send_message(chat_id=ID, text='Вы отказали в соединении.')
        if not info_key["request_answer"] == "unknown":
            if info_key["request_answer"] == "yes":
                bot.send_message(chat_id=key, text="Пользователь отказал в соединении.")
            info_id["request_answer"] = "unknown"
            info_key["request_answer"] = "unknown"



@bot.callback_query_handler(func=lambda call: 'yes' in call.data or 'no' in call.data)
def consent_to_connect(call):
    with shelve.open('info', writeback=True) as info:
        ID = str(call.message.chat.id)
        key = call.data.split()[-1] if call.data.split()[-1] != ID else call.data.split()[-2]
        consent_to_connect_act(info[ID], info[key], ID, key, call.message.message_id, call.data.split())


def black_list_act(info_id, answer, ID):
    if answer == 'нет':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text='Да', callback_data='1 signal'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Нет', callback_data='0 signal'))
        bot.send_message(chat_id=ID,
                         text="Подходящий пользователь не найден. Соединить ли вас при появлении подходящего пользователя?",
                         reply_markup=keyboard)
    else:
        info_id["black_list"] = []
        bot.send_message(chat_id=ID, text="Черный список очищен. Нажмите /search, чтобы запустить поиск. ")


@bot.callback_query_handler(func=lambda call: 'да' in call.data or 'нет' in call.data)
def black_list(call):
    with shelve.open('info', writeback=True) as info:
        ID = str(call.message.chat.id)
        bot.delete_message(chat_id=ID, message_id=call.message.message_id)
        black_list_act(info[ID], call.data, ID)


def signal_act(info_id, ID, answer):
    if answer == "0":
        info_id["signal"] = "0"
    else:
        bot.send_message(chat_id=ID, text="Подождите, пока пользователь не появится.")


@bot.callback_query_handler(func=lambda call: 'signal' in call.data)
def signal(call):
    with shelve.open('info', writeback=True) as info:
        ID = str(call.message.chat.id)
        bot.delete_message(chat_id=ID, message_id=call.message.message_id)
        signal_act(info[ID], ID, call.data[:call.data.find("s") - 1])




@bot.message_handler(commands=['search'])
def search(message):
    ID = str(message.chat.id)
    with shelve.open('info', writeback=True) as info:
        info[ID]["signal"] = "1"
        keys = info.keys()
        for key in keys:
            try:
                if info[ID]['signal'] == '1':
                    # Поиск подходящего пользователя:
                    if info[key]["signal"] == '1' and \
                            key != ID and \
                            info[key]["my_profile"]["gender"] in info[ID]["find"]["gender"] and \
                            int(info[ID]["find"]["age_to"]) >= int(info[key]["my_profile"]["age"]) >= int(
                        info[ID]["find"]["age_from"]) and \
                            info[ID]["my_profile"]["gender"] in info[key]["find"]["gender"] and \
                            int(info[key]["find"]["age_from"]) <= int(info[ID]["my_profile"]["age"]) <= int(
                        info[key]["find"]["age_to"]) and not \
                            key in info[ID]['black_list']:
                        info[key]["action"] = "7"
                        info[ID]["action"] = "7"
                        keyboard = telebot.types.InlineKeyboardMarkup()
                        keyboard.add(telebot.types.InlineKeyboardButton(text='Да', callback_data=f'yes {key} {ID}'))
                        keyboard.add(telebot.types.InlineKeyboardButton(text='Нет', callback_data='no'))
                        bot.send_message(chat_id=ID, text=f'Найден пользователь:\n'
                                                          f'Пол: {info[key]["my_profile"]["gender"]}\n\n'
                                                          f'Возраст: {info[key]["my_profile"]["age"]}\n\n'
                                                          f'О себе: {info[key]["my_profile"]["info"]}', )
                        bot.send_message(chat_id=ID, text="Соединить вас с ним?", reply_markup=keyboard)
                        bot.send_message(chat_id=key, text=f'Найден пользователь:\n'
                                                           f'Пол: {info[ID]["my_profile"]["gender"]}\n\n'
                                                           f'Возраст: {info[ID]["my_profile"]["age"]}\n\n'
                                                           f'О себе: {info[ID]["my_profile"]["info"]}', )
                        bot.send_message(chat_id=key, text="Соединить вас с ним?", reply_markup=keyboard)
                        break
            except:
                break
        else:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text='Да', callback_data='да'))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Нет', callback_data='нет'))
            bot.send_message(chat_id=ID,
                             text="Подходящий пользователь не найден. Хотите ли вы очистить ваш черный список? "
                                  "В таком случае мы, возможно, сможем найти подходящего пользователя из ваших предыдущих собеседников. ",
                             reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def text(message):
    ID = str(message.chat.id)
    with shelve.open('info', writeback=True) as info:
        if info[ID]["action"] == "1" and message.text.isdigit() and len(message.text) < 3:
            info[ID]["action"] = "2"
            info[ID]["my_profile"]["age"] = message.text
            bot.send_message(chat_id=ID, text='Расскажите о себе: ')
        elif info[ID]["action"] in ["1", "3", "4"] and not message.text.isdigit():
            bot.send_message(chat_id=ID, text='Введите цифры, пожалуйста: ')
        elif info[ID]["action"] in ["1", "3", "4"] and len(message.text) > 2:
            bot.send_message(chat_id=ID, text="Это явно не человеческий возраст. Попробуйте снова: ")
        elif info[ID]["action"] == '2':
            if len(message.text) >= 20:
                info[ID]["action"] = "10"
                info[ID]["my_profile"]["info"] = message.text
                bot.send_message(chat_id=ID, text='Информация сохранена.')
                bot.send_message(chat_id=ID,
                                 text="Нажмите /who_i_need, чтобы указать требования к анкете пользователя-собеседника.")
            else:
                bot.send_message(chat_id=ID, text='Слишком коротко. Попробуйте снова: ')
        elif info[ID]["action"] == "3":
            info[ID]["find"]["age_from"] = message.text
            keyboard = telebot.types.InlineKeyboardMarkup()
            for x in range(6, 61, 6):
                keyboard.row(telebot.types.InlineKeyboardButton(text=str(x), callback_data=str(x) + 'find_to_age'),
                             telebot.types.InlineKeyboardButton(text=str(x + 1),
                                                                callback_data=str(x + 1) + 'find_to_age'),
                             telebot.types.InlineKeyboardButton(text=str(x + 2),
                                                                callback_data=str(x + 2) + 'find_to_age'),
                             telebot.types.InlineKeyboardButton(text=str(x + 3),
                                                                callback_data=str(x + 3) + 'find_to_age'),
                             telebot.types.InlineKeyboardButton(text=str(x + 4),
                                                                callback_data=str(x + 4) + 'find_to_age'),
                             telebot.types.InlineKeyboardButton(text=str(x + 5),
                                                                callback_data=str(x + 5) + 'find_to_age')
                             )
            keyboard.add(telebot.types.InlineKeyboardButton(text="Другой возраст (указать самостоятельно)",
                                                            callback_data="d_age find_to_age"))
            bot.send_message(chat_id=ID, text="Укажите верхнюю возрастную границу: ", reply_markup=keyboard)
            info[ID]["action"] = "10"
        elif info[ID]["action"] == "4":
            info[ID]["action"] = "10"
            info[ID]["find"]["age_to"] = message.text
            bot.send_message(chat_id=ID, text="Информация сохранена.")
            bot.send_message(chat_id=ID, text="Нажмите /search, чтобы начать поиск подходящего собеседника.")
        else:
            if info[ID]["other_id"]:
                if time.time() - float(info[info[ID]["other_id"]]["my_time"]["time"]) > 60 \
                        and info[info[ID]["other_id"]]["my_time"]["flag"] == "0":
                    bot.send_message(chat_id=ID, text='Вашего собеседника нет уже больше минуты.'
                                                      '\nНапоминаю, что с помощью команды /leave_chat вы можете разорвать соединение.')
                    bot.send_message(chat_id=info[ID]["other_id"], text="Вас нет уже больше минуты.\n"
                                                                        "Помните, что собеседник может не дождаться вас и разорвать соединение.")
                    info[info[ID]["other_id"]]["my_time"]["flag"] = "1"
                bot.send_message(chat_id=info[ID]["other_id"], text="Ваш собеседник пишет:\n\n_" + message.text + "_",
                                 parse_mode="Markdown")
                info[ID]['my_time']["time"] = str(time.time())


if __name__ == '__main__':
    bot.polling()
