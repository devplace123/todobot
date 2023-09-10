import telebot
from telebot.types import ReplyKeyboardMarkup
import requests
import json
from telebot import types

bot = telebot.TeleBot('6565647962:AAETwRY74XoIughyVPVnTVJizMP07HU-2KQ')

name = ''
last_name = ''
email = ''


@bot.message_handler()
def start(message):
    if message.text == '/start':
        k = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        k.row('Зарегистрироваться')
        bot.send_message(message.chat.id, 'Добро пожаловать в бот!',
                         reply_markup= k)
    elif message.text == 'Зарегистрироваться':
        m = bot.send_message(message.chat.id, 'Введите ваше имя')
        bot.register_next_step_handler(m, get_name)

    elif message.text == 'Сгенерировать пригласительный код':
        resp = requests.post('http://127.0.0.1:8000/getinvite/', data={'chat_id':message.chat.id})
        bot.send_message(message.chat.id, f'''Ваш пригласительный код - {json.loads(resp.content)[0]['fields']['code']}''')

    elif message.text == 'Ввести пригласительный код':
        pass

    elif message.text == 'Добавить задачу':
        m = bot.send_message(message.chat.id, 'Введите название задачи')
        bot.register_next_step_handler(m, get_task_name)

    elif message.text == 'Получить актуальные задачи':
        resp = requests.post(f'http://127.0.0.1:8000/get/actual/{message.chat.id}').content
        for i in json.loads(resp):
            bot.send_message(message.chat.id, f'{i["fields"]["name"]}\n{i["fields"]["text"]}')

    elif message.text == 'Получить неактуальные задачи':
        resp = requests.post(f'http://127.0.0.1:8000/get/notactual/{message.chat.id}').content
        for i in json.loads(resp):
            k = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton('Выполнено', callback_data=i['pk'])
            k.add(btn)
            bot.send_message(message.chat.id, f'{i["fields"]["name"]}\n{i["fields"]["text"]}', reply_markup=k)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    print(call.data)
    requests.post('http://127.0.0.1:8000/set/notactual/', data={'id':call.data})
    bot.send_message(call.message.chat.id, 'Задача выполнена!\nВот список актуальных на текущий момент задач')
    resp = requests.post(f'http://127.0.0.1:8000/get/actual/{call.message.chat.id}').content
    for i in json.loads(resp):
        k = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton('Выполнено', callback_data=i['pk'])
        k.add(btn)
        bot.send_message(call.message.chat.id, f'{i["fields"]["name"]}\n{i["fields"]["text"]}', reply_markup=k)

def get_task_name(message):
    global name
    name = message.text
    m = bot.send_message(message.chat.id, 'Введите текст задачи')
    bot.register_next_step_handler(m, get_task_text)


def get_task_text(message):
    c = requests.post('http://127.0.0.1:8000/addtask/', data={'name':name, 'text':message.text, 'chat_id':message.chat.id})
    if c.status_code == 200:
        bot.send_message(message.chat.id, 'Задача создана успешно')


def get_name(message):
    global name
    name = message.text
    m = bot.send_message(message.chat.id, 'Введите вашу фамилию')
    bot.register_next_step_handler(m, get_lastname)

def get_lastname(message):
    global last_name
    last_name = message.text
    m = bot.send_message(message.chat.id, 'Введите ваш email')
    bot.register_next_step_handler(m, get_email)


def get_email(message):
    global email
    email = message.text
    if '@' not in email:
        m = bot.send_message(message.chat.id, 'Ваш email введен неверно. Повторите ввод')
        bot.register_next_step_handler(m, get_email)
        return 0
    k = ReplyKeyboardMarkup()
    k.row('Добавить задачу', 'Ввести пригласительный код')
    k.row('Сгенерировать пригласительный код', 'Получить актуальные задачи')
    k.row('Получить неактуальные задачи')
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=
                     k)
    c = requests.post('http://127.0.0.1:8000/adduser/', data={'chat_id':message.chat.id,
                                                          'name':name,
                                                          'lastname':last_name,
                                                          'email':email}).content
    print(c)


bot.polling()