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
        info[ID] = {"action": "0",
                    "my_profile": {"gender": "", "age": "", "info": ""},
                    "find": {"gender": '', "age_from": '', "age_to": ''},
                    "other_id": '',
                    "black_list": [],
                    "signal": '0',
                    "request_answer": "unknown",
                    "my_time": ""}
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text='Женский', callback_data='Женский my_gender'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Мужской', callback_data='Мужской my_gender'))
        bot.delete_message(ID, message.message_id)
        bot.send_message(chat_id=ID, text='Выберите ваш пол: ', reply_markup=keyboard)


@bot.message_handler(commands=['my_profile'])
def my_profile(message):
    ID = str(message.chat.id)
    with shelve.open('info') as info:
        print(info[ID])
        bot.delete_message(ID, message.message_id)


@bot.message_handler(commands=['who_i_need'])
def who(message):
    ID = str(message.chat.id)
    with shelve.open('info', writeback=True) as info:
        info[ID]["action"] = "3"
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text='Женский', callback_data='Женский find_gender'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Мужской', callback_data='Мужской find_gender'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Не имеет значения', callback_data='Женский Мужской find_gender'))
        bot.delete_message(chat_id=ID, message_id=message.message_id)
        bot.send_message(chat_id=ID, text='Выберите желаемый пол:', reply_markup=keyboard)


@bot.message_handler(commands=['leave_chat'])
def leave_chat(message):
    ID = str(message.chat.id)
    with shelve.open('info', writeback=True) as info:
        info[ID]['black_list'] = info[ID]["black_list"] + info[ID]["other_id"]
        info[ID]['other_id'] = ''
        bot.delete_message(ID, message.message_id)
        bot.send_message(chat_id=ID, text="Вы вышли из чата.")


# Выделить функции
# Обработчики событий разделить
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
        my_profile_gender(info[ID], call.data[:call.data.find('m') - 1], ID, call.message.message_id, keyboard)


def my_profile_age(info_id, age, ID, message_id):
    info_id["action"] = "3"
    info_id["my_profile"]["age"] = age
    bot.delete_message(chat_id=ID, message_id=message_id)
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
    bot.send_message(chat_id=ID, text="Укажите верхнюю возрастную границу:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: 'find_gender' in call.data)
def find_gender(call):
    with shelve.open('info', writeback=True) as info:
        ID = str(call.message.chat.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        for x in range(6, 61, 6):
            keyboard.row(telebot.types.InlineKeyboardButton(text=str(x), callback_data=str(x) + 'find_from_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 1), callback_data=str(x + 1) + 'find_from_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 2), callback_data=str(x + 2) + 'find_from_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 3), callback_data=str(x + 3) + 'find_from_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 4), callback_data=str(x + 4) + 'find_from_age'),
                         telebot.types.InlineKeyboardButton(text=str(x + 5), callback_data=str(x + 5) + 'find_from_age')
                         )
        find_gender_act(info[ID], call.data[:call.data.find('f') - 1], ID, call.message.message_id, keyboard)


def find_from_age_act(info_id, from_age, ID, message_id, keyboard):
    info_id["find"]["age_from"] = from_age
    bot.delete_message(chat_id=ID, message_id=message_id)
    bot.send_message(chat_id=ID, text='Укажите нижнюю возрастную границу: ', reply_markup=keyboard)


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
        find_from_age_act(info[ID], call.data[:call.data.find('f')], ID, call.message.message_id, keyboard)


def find_to_age_act(info_id, to_age, ID, message_id):
    info_id["find"]["age_to"] = to_age
    bot.delete_message(chat_id=ID, message_id=message_id)
    bot.send_message(chat_id=ID, text='Информация сохранена.')


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
        elif info_key['request_answer'] == 'yes':
            info_key["other_id"] = ID
            info_key["signal"] = "0"
            info_key["request_answer"] = "unknown"
            info_id["other_id"] = key
            info_id["signal"] = "0"
            info_id["request_answer"] = "unknown"
            bot.send_message(chat_id=ID, text='Соединение установлено.')
            bot.send_message(chat_id=key, text='Соединение установлено.')
            info_id['my_time'] = str(time.time())
            info_key['my_time'] = str(time.time())
            my_difference = time.time() - float(info_id['my_time'])
            key_difference = time.time() - float(info_key['my_time'])
            while my_difference < 120 and key_difference < 120:
                bot.send_message(chat_id=ID, text=str(my_difference) + ' ' + str(key_difference))
                bot.send_message(chat_id=ID, text=info_id['my_time'] + info_key['my_time'])
                if my_difference >= 60 > my_difference - 10:
                    bot.send_message(chat_id=ID, text="У вас осталась минута, чтобы написать что-нибудь, иначе связь будет разорвана.")
                if key_difference >= 60 > key_difference - 10:
                    bot.send_message(chat_id=key, text='У вас осталась минута, чтобы написать что-нибудь, иначе связь будет разорвана.')
                time.sleep(10)
                try:
                    my_difference = time.time() - float(info_id['my_time'])
                    key_difference = time.time() - float(info_key['my_time'])
                except:
                    pass
            info_key["other_id"] = ''
            info_id["other_id"] = ''
            bot.send_message(chat_id=ID, text='Соединение разорвано.')
            bot.send_message(chat_id=key, text='Соединение разорвано.')
        elif info_key['request_answer'] == 'unknown':
            bot.send_message(chat_id=ID, text='Пользователь еще не дал ответ. Пожалуйста, подождите.')
    else:
        info_id["signal"] = "0"
        info_id["request_answer"] = "unknown"
        bot.send_message(chat_id=ID, text='Вы отказали в соединении.')


@bot.callback_query_handler(func=lambda call: 'yes' in call.data or 'no' in call.data)
@telebot.util.async_dec()
def consent_to_connect(call):
    with shelve.open('info', writeback=True) as info:
        ID = str(call.message.chat.id)
        key = call.data.split()[-1] if call.data.split()[-1] != ID else call.data.split()[-2]
        consent_to_connect_act(info[ID], info[key], ID, key, call.message.message_id, call.data.split())


def signal_act(info_id, answer):
    if answer == 'нет':
        info_id['signal'] = '0'


@bot.callback_query_handler(func=lambda call: 'да' in call.data or 'нет' in call.data)
def signal(call):
    with shelve.open('info', writeback=True) as info:
        ID = str(call.message.chat.id)
        bot.delete_message(chat_id=ID, message_id=call.message.message_id)
        signal_act(info[ID], call.data)


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
                        bot.send_message(chat_id=ID, text=f'Найден пользователь:\n '
                                                          f'Пол: {info[key]["my_profile"]["gender"]}\n\n'
                                                          f'Возраст: {info[key]["my_profile"]["age"]}\n\n'
                                                          f'О себе: {info[key]["my_profile"]["info"]}')
                        bot.send_message(chat_id=ID, text="Соединить вас с ним?", reply_markup=keyboard)
                        bot.send_message(chat_id=key, text=f'Найден пользователь:\n'
                                                           f'Пол: {info[ID]["my_profile"]["gender"]}\n\n'
                                                           f'Возраст: {info[ID]["my_profile"]["age"]}\n\n'
                                                           f'О себе: {info[ID]["my_profile"]["info"]}')
                        bot.send_message(chat_id=key, text="Соединить вас с ним?", reply_markup=keyboard)
                        break
            except:
                break
        else:
            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.add(telebot.types.InlineKeyboardButton(text='Да', callback_data='да'))
            keyboard.add(telebot.types.InlineKeyboardButton(text='Нет', callback_data='нет'))
            bot.send_message(chat_id=ID,
                             text="Подходящий пользователь не найден. Соединить ли вас при появлении подходящего пользователя?",
                             reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
@telebot.util.async_dec()
def text(message):
    ID = str(message.chat.id)
    with shelve.open('info', writeback=True) as info:
        if info[ID]["action"] == "1" and message.text.isdigit():
            info[ID]["action"] = "2",
            info[ID]["my_profile"]["age"] = message.text
            bot.send_message(chat_id=ID, text='Расскажите о себе: ')
        elif info[ID]["action"] == '1' and not message.text.isdigit():
            bot.send_message(chat_id=ID, text='Введите цифры, пожалуйста: ')
        elif info[ID]["action"] == '2':
            if len(message.text) >= 20:
                info[ID]["action"] = "10"
                info[ID]["my_profile"]["info"] = message.text
                bot.send_message(chat_id=ID, text='Информация сохранена.')
            else:
                bot.send_message(chat_id=ID, text='Слишком коротко. Попробуйте снова: ')
        else:
            if info[ID]["other_id"]:
                bot.send_message(chat_id=info[ID]["other_id"], text=message.text)
                info[ID]['my_time'] = str(time.time())


if __name__ == '__main__':
    bot.polling()
