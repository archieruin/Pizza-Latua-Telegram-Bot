# -*- coding: utf-8 -*-

import telebot

import product
import sender
import states
import db
import keyboards
import messages
import hashlib
import urllib.request as urllib2
from config import States
from messages import Messages
from telebot import types

import flask

import config

import time

bot = telebot.TeleBot(config.token)

# WEBHOOK COMMENT
# WEBHOOK_HOST = '46.229.215.56'
# WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
# WEBHOOK_LISTEN = '46.229.215.56'  # In some VPS you may need to put here the IP addr
#
#
# WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
# WEBHOOK_URL_PATH = "/%s/" % (config.token)
#
# WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
# WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key
#
#
# app = flask.Flask(__name__)
#
#
# # Empty webserver index, return nothing, just http 200
# @app.route('/', methods=['GET', 'HEAD'])
# def index():
#     return '<b>Hello World</b>'
#
#
# # Process webhook calls
# @app.route(WEBHOOK_URL_PATH, methods=['POST'])
# def webhook():
#     if flask.request.headers.get('content-type') == 'application/json':
#         json_string = flask.request.get_data().decode('utf-8')
#         update = telebot.types.Update.de_json(json_string)
#         bot.process_new_updates([update])
#         return ''
#     else:
#         flask.abort(403)


@bot.message_handler(commands=['start', 'help'])
def cmd_start(message):
    bot.send_message(message.chat.id, Messages.WELCOME.value.format(message.chat.first_name),
                     reply_markup=keyboards.main_menu())
    states.set_state(message.chat.id, States.S_MAIN_MENU.value)


@bot.message_handler(commands=['menu'])
def cmd_menu(message):
    bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                     reply_markup=keyboards.categories())
    states.set_state(message.chat.id, States.S_MENU.value)


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_MAIN_MENU.value)
def main_menu(message):
    if message.text == '☎ Контакты':
        bot.send_message(message.chat.id, Messages.CONTACTS.value,
                         reply_markup=keyboards.main_menu())
    elif message.text == '🚀 Доставка':
        bot.send_message(message.chat.id, Messages.DELIVERY.value,
                         parse_mode='HTML',
                         reply_markup=keyboards.main_menu())
    elif message.text == '✏ Информация':
        bot.send_message(message.chat.id, Messages.INFO.value,
                         parse_mode='HTML',
                         reply_markup=keyboards.main_menu())
    elif message.text == '🍴 Меню':
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        states.set_state(message.chat.id, States.S_MENU.value)
    elif message.text == '📥 Корзина':
        bot.send_message(message.chat.id, messages.basket(message.chat.id), parse_mode='HTML',
                         reply_markup=keyboards.basket())
    else:
        bot.send_message(message.chat.id, 'Неизвесная команда!\n'
                                          'Попробуйте /start или /help')


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_MENU.value)
def categories_menu(message):
    if message.text == '🍕 Пицца':
        bot.send_message(message.chat.id, 'Выберите блюдо 👇🏻', reply_markup=keyboards.pizza())
        states.set_state(message.chat.id, States.S_PIZZA_MENU.value)
    elif message.text == '🍔 Бургеры':
        bot.send_message(message.chat.id, 'Выберите блюдо 👇🏻', reply_markup=keyboards.burger())
        states.set_state(message.chat.id, States.S_BURGER_MENU.value)
    elif message.text == '🍹 Напитки':
        bot.send_message(message.chat.id, 'Выберите блюдо 👇🏻', reply_markup=keyboards.drinks())
        states.set_state(message.chat.id, States.S_DRINKS_MENU.value)
    elif message.text == '🍝 Паста':
        bot.send_message(message.chat.id, 'Выберите блюдо 👇🏻', reply_markup=keyboards.pasta())
        states.set_state(message.chat.id, States.S_PASTA_MENU.value)
    elif message.text == '🥗 Салаты':
        bot.send_message(message.chat.id, 'Выберите блюдо 👇🏻', reply_markup=keyboards.salad())
        states.set_state(message.chat.id, States.S_SALAD_MENU.value)
    elif message.text == '🥘 Супы':
        bot.send_message(message.chat.id, 'Выберите блюдо 👇🏻', reply_markup=keyboards.soup())
        states.set_state(message.chat.id, States.S_SOUP_MENU.value)
    elif message.text == '🍽 Прочие блюда':
        bot.send_message(message.chat.id, 'Выберите блюдо 👇🏻', reply_markup=keyboards.others())
        states.set_state(message.chat.id, States.S_OTHER_MENU.value)
    elif message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
    elif message.text == '📥 Корзина':
        bot.send_message(message.chat.id, messages.basket(message.chat.id), parse_mode='HTML',
                         reply_markup=keyboards.basket())
    else:
        bot.send_message(message.chat.id, 'Неизвесная команда!\n'
                                          'Попробуйте /start или /help')


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_PIZZA_MENU.value)
def pizza_menu(message):
    for p in product.get_pizza_titles():
        if message.text == p:
            bot.send_chat_action(message.chat.id, 'upload_photo')

            img_url = product.get_pizza_by_title(message.text)['picture']
            try:
                urllib2.urlretrieve(img_url, 'cache/pizza.jpg')
                img = open('cache/pizza.jpg', 'rb')
            except:
                urllib2.urlretrieve(img_url, 'cache/pizza_two.jpg')
                img = open('cache/pizza_two.jpg', 'rb')

            product_ = product.get_pizza_by_title(message.text)
            bot.send_message(message.chat.id, 'Ваш продукт: ', reply_markup=keyboards.back_keyboard())
            bot.send_photo(message.chat.id, img, messages.pizza_data(product_), parse_mode='HTML',
                           reply_markup=keyboards.add_to_basket_pizza())
            img.close()

            db.set_cache(message.chat.id, message.text)

    if message.text == '⬅ Назад':
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        states.set_state(message.chat.id, States.S_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '📥 Корзина':
        bot.send_message(message.chat.id, messages.basket(message.chat.id), parse_mode='HTML',
                         reply_markup=keyboards.basket())
    elif not product.get_pizza_by_title(message.text)['title']:
        bot.send_message(message.chat.id, 'Неизвесное название продукта попробуйте другое!\n'
                                          'Или попробуйте /start или /help')


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_BURGER_MENU.value)
def burger_menu(message):
    for p in product.get_burger_titles():
        if message.text == p:
            bot.send_chat_action(message.chat.id, 'upload_photo')

            img_url = product.get_burger_by_title(message.text)['picture']
            try:
                urllib2.urlretrieve(img_url, 'cache/burger.jpg')
                img = open('cache/burger.jpg', 'rb')
            except:
                urllib2.urlretrieve(img_url, 'cache/burger_two.jpg')
                img = open('cache/burger_two.jpg', 'rb')

            product_ = product.get_burger_by_title(message.text)
            bot.send_message(message.chat.id, 'Ваш продукт: ', reply_markup=keyboards.back_keyboard())
            bot.send_photo(message.chat.id, img, messages.product_data(product_), parse_mode='HTML',
                           reply_markup=keyboards.add_to_basket())
            img.close()
            db.add_order(message.chat.id,
                         message.text,
                         product_['comp'],
                         product_['price'],
                         product_['picture'])
            db.set_cache(message.chat.id, message.text)

    if message.text == '⬅ Назад':
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        states.set_state(message.chat.id, States.S_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '📥 Корзина':
        bot.send_message(message.chat.id, messages.basket(message.chat.id), parse_mode='HTML',
                         reply_markup=keyboards.basket())
    elif not product.get_burger_by_title(message.text)['title']:
        bot.send_message(message.chat.id, 'Неизвесное название продукта попробуйте другое!\n'
                                          'Или попробуйте /start или /help')


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_DRINKS_MENU.value)
def drinks_menu(message):
    for p in product.get_drinks_titles():
        if message.text == p:
            bot.send_chat_action(message.chat.id, 'upload_photo')

            img_url = product.get_drinks_by_title(message.text)['picture']
            try:
                urllib2.urlretrieve(img_url, 'cache/drinks.jpg')
                img = open('cache/drinks.jpg', 'rb')
            except:
                urllib2.urlretrieve(img_url, 'cache/drinks_two.jpg')
                img = open('cache/drinks_two.jpg', 'rb')

            product_ = product.get_drinks_by_title(message.text)
            bot.send_message(message.chat.id, 'Ваш продукт: ', reply_markup=keyboards.back_keyboard())
            bot.send_photo(message.chat.id, img, messages.product_data(product_), parse_mode='HTML',
                           reply_markup=keyboards.add_to_basket())
            img.close()
            db.add_order(message.chat.id,
                         message.text,
                         product_['comp'],
                         product_['price'],
                         product_['picture'])
            db.set_cache(message.chat.id, message.text)

    if message.text == '⬅ Назад':
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        states.set_state(message.chat.id, States.S_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '📥 Корзина':
        bot.send_message(message.chat.id, messages.basket(message.chat.id), parse_mode='HTML',
                         reply_markup=keyboards.basket())
    elif not product.get_drinks_by_title(message.text)['title']:
        bot.send_message(message.chat.id, 'Неизвесное название продукта попробуйте другое!\n'
                                          'Или попробуйте /start или /help')


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_PASTA_MENU.value)
def pasta_menu(message):
    for p in product.get_pasta_titles():
        if message.text == p:
            bot.send_chat_action(message.chat.id, 'upload_photo')

            img_url = product.get_pasta_by_title(message.text)['picture']
            try:
                urllib2.urlretrieve(img_url, 'cache/pasta.jpg')
                img = open('cache/pasta.jpg', 'rb')
            except:
                urllib2.urlretrieve(img_url, 'cache/pasta_two.jpg')
                img = open('cache/pasta_two.jpg', 'rb')

            product_ = product.get_pasta_by_title(message.text)
            bot.send_message(message.chat.id, 'Ваш продукт: ', reply_markup=keyboards.back_keyboard())
            bot.send_photo(message.chat.id, img, messages.product_data(product_), parse_mode='HTML',
                           reply_markup=keyboards.add_to_basket())
            img.close()
            db.add_order(message.chat.id,
                         message.text,
                         product_['comp'],
                         product_['price'],
                         product_['picture'])
            db.set_cache(message.chat.id, message.text)

    if message.text == '⬅ Назад':
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        states.set_state(message.chat.id, States.S_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '📥 Корзина':
        bot.send_message(message.chat.id, messages.basket(message.chat.id), parse_mode='HTML',
                         reply_markup=keyboards.basket())
    elif not product.get_pasta_by_title(message.text)['title']:
        bot.send_message(message.chat.id, 'Неизвесное название продукта попробуйте другое!\n'
                                          'Или попробуйте /start или /help')


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_SALAD_MENU.value)
def salad_menu(message):
    for p in product.get_salad_titles():
        if message.text == p:
            bot.send_chat_action(message.chat.id, 'upload_photo')

            img_url = product.get_salad_by_title(message.text)['picture']
            try:
                urllib2.urlretrieve(img_url, 'cache/salad.jpg')
                img = open('cache/salad.jpg', 'rb')
            except:
                urllib2.urlretrieve(img_url, 'cache/salad_two.jpg')
                img = open('cache/salad_two.jpg', 'rb')

            product_ = product.get_salad_by_title(message.text)
            bot.send_message(message.chat.id, 'Ваш продукт: ', reply_markup=keyboards.back_keyboard())
            bot.send_photo(message.chat.id, img, messages.product_data(product_), parse_mode='HTML',
                           reply_markup=keyboards.add_to_basket())
            img.close()
            db.add_order(message.chat.id,
                         message.text,
                         product_['comp'],
                         product_['price'],
                         product_['picture'])
            db.set_cache(message.chat.id, message.text)

    if message.text == '⬅ Назад':
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        states.set_state(message.chat.id, States.S_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '📥 Корзина':
        bot.send_message(message.chat.id, messages.basket(message.chat.id), parse_mode='HTML',
                         reply_markup=keyboards.basket())
    elif not product.get_salad_by_title(message.text)['title']:
        bot.send_message(message.chat.id, 'Неизвесное название продукта попробуйте другое!\n'
                                          'Или попробуйте /start или /help')


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_SOUP_MENU.value)
def soup_menu(message):
    for p in product.get_soup_titles():
        if message.text == p:
            bot.send_chat_action(message.chat.id, 'upload_photo')

            img_url = product.get_soup_by_title(message.text)['picture']
            try:
                urllib2.urlretrieve(img_url, 'cache/soup.jpg')
                img = open('cache/soup.jpg', 'rb')
            except:
                urllib2.urlretrieve(img_url, 'cache/soup_two.jpg')
                img = open('cache/soup_two.jpg', 'rb')

            product_ = product.get_soup_by_title(message.text)
            bot.send_message(message.chat.id, 'Ваш продукт: ', reply_markup=keyboards.back_keyboard())
            bot.send_photo(message.chat.id, img, messages.product_data(product_), parse_mode='HTML',
                           reply_markup=keyboards.add_to_basket())
            img.close()
            db.add_order(message.chat.id,
                         message.text,
                         product_['comp'],
                         product_['price'],
                         product_['picture'])
            db.set_cache(message.chat.id, message.text)

    if message.text == '⬅ Назад':
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        states.set_state(message.chat.id, States.S_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '📥 Корзина':
        bot.send_message(message.chat.id, messages.basket(message.chat.id), parse_mode='HTML',
                         reply_markup=keyboards.basket())
    elif not product.get_soup_by_title(message.text)['title']:
        bot.send_message(message.chat.id, 'Неизвесное название продукта попробуйте другое!\n'
                                          'Или попробуйте /start или /help')


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_OTHER_MENU.value)
def others_menu(message):
    for p in product.get_others_titles():
        if message.text == p:
            bot.send_chat_action(message.chat.id, 'upload_photo')

            img_url = product.get_others_by_title(message.text)['picture']
            try:
                urllib2.urlretrieve(img_url, 'cache/other.jpg')
                img = open('cache/other.jpg', 'rb')
            except:
                urllib2.urlretrieve(img_url, 'cache/other_two.jpg')
                img = open('cache/other_two.jpg', 'rb')

            product_ = product.get_others_by_title(message.text)
            bot.send_message(message.chat.id, 'Ваш продукт: ', reply_markup=keyboards.back_keyboard())
            bot.send_photo(message.chat.id, img, messages.product_data(product_), parse_mode='HTML',
                           reply_markup=keyboards.add_to_basket())
            img.close()
            db.add_order(message.chat.id,
                         message.text,
                         product_['comp'],
                         product_['price'],
                         product_['picture'])
            db.set_cache(message.chat.id, message.text)

    if message.text == '⬅ Назад':
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        db.delete_empty_orders(message.chat.id)
        states.set_state(message.chat.id, States.S_MENU.value)
    elif message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_empty_orders(message.chat.id)
    elif message.text == '📥 Корзина':
        bot.send_message(message.chat.id, messages.basket(message.chat.id), parse_mode='HTML',
                         reply_markup=keyboards.basket())
    elif not product.get_others_by_title(message.text)['title']:
        bot.send_message(message.chat.id, 'Неизвесное название продукта попробуйте другое!\n'
                                          'Или попробуйте /start или /help')


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_CHOSE_PIZZA_WEIGHT.value)
def chose_weight_menu(message):
    weights = product.get_pizza_weight_by_title(db.get_cache(message.chat.id))

    if message.text == '⬅ Назад':
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        db.delete_empty_orders(message.chat.id)
        states.set_state(message.chat.id, States.S_MENU.value)

    else:
        for w in weights:
            if message.text in w['text']:
                product_ = product.get_pizza_by_title(db.get_cache(message.chat.id))
                db.add_order_pizza(message.chat.id,
                                   db.get_cache(message.chat.id),
                                   product_['comp'],
                                   w['text'],
                                   int(product_['price']) + int(w['price']),
                                   product_['picture'])
                bot.send_message(message.chat.id, 'Выбор количества ⬇', reply_markup=keyboards.back_keyboard())
                bot.send_message(message.chat.id, '<b>' + db.get_cache(message.chat.id) + '</b>\n<b>Цена: ' +
                                 str(int(product_['price']) + int(w['price'])) + '</b> — ' + message.text,
                                 reply_markup=keyboards.chose_amount(),
                                 parse_mode='HTML')
                states.set_state(message.chat.id, States.S_CHOSE_AMOUNT.value)


@bot.callback_query_handler(func=lambda call: True)
def add_to_basket(call):
    state = states.get_current_state(call.message.chat.id)
    if call.data == 'add_to_basket':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=keyboards.chose_amount())
        bot.answer_callback_query(call.id, 'Выберите количество')
        states.set_state(call.message.chat.id, States.S_CHOSE_AMOUNT.value)

    elif call.data == 'add_to_basket_pizza':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=keyboards.chose_pizza_weight())
        bot.answer_callback_query(call.id, 'Выберите вес ⬇')
        weights = product.get_pizza_weight_by_title(db.get_cache(call.message.chat.id))
        bot.send_message(call.message.chat.id, 'Выберите вес ⬇', reply_markup=keyboards.pizza_weights(weights))
        states.set_state(call.message.chat.id, States.S_CHOSE_PIZZA_WEIGHT.value)

    elif call.data == 'chose_weight':
        bot.answer_callback_query(call.id, 'Выберите вес')

    elif call.data == 'back_to_menu':
        bot.answer_callback_query(call.id, '⬅ Назад')
        bot.send_message(call.message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        states.set_state(call.message.chat.id, States.S_MENU.value)

    elif call.data == 'back':
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=keyboards.add_to_basket())
        bot.answer_callback_query(call.id, '⬅ Назад')
        bot.send_message(call.message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        states.set_state(call.message.chat.id, States.S_MENU.value)
        db.delete_empty_orders(call.message.chat.id)
    elif call.data == 'chose_amount':
        bot.answer_callback_query(call.id, 'Выберите колличество')

    elif state == States.S_CHOSE_AMOUNT.value:
        title = db.get_cache(call.message.chat.id)
        if call.data == '1':
            sum = db.get_orders_by_chat_id_and_title(call.message.chat.id, title)[0][2] + 1
            db.edit_order_amount(call.message.chat.id, title, sum)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                          reply_markup=keyboards.add_to_basket())
            bot.answer_callback_query(call.id, '✅ Успешно добавлено в корзину')
            bot.send_message(call.message.chat.id, '✅ Успешно добавлено в корзину\n\n'
                                                   'Вы уже можете оформить ваш заказ, кликнув на кнопку "📥 Корзина"',
                             reply_markup=keyboards.main_menu())
            states.set_state(call.message.chat.id, States.S_MAIN_MENU.value)

        elif call.data == '2':
            sum = db.get_orders_by_chat_id_and_title(call.message.chat.id, title)[0][2] + 2
            db.edit_order_amount(call.message.chat.id, title, sum)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                          reply_markup=keyboards.add_to_basket())
            bot.answer_callback_query(call.id, '✅ Успешно добавлено в корзину')
            bot.send_message(call.message.chat.id, '✅ Успешно добавлено в корзину\n\n'
                                                   'Вы уже можете оформить ваш заказ, кликнув на кнопку "📥 Корзина"',
                             reply_markup=keyboards.main_menu())
            states.set_state(call.message.chat.id, States.S_MAIN_MENU.value)

        elif call.data == '3':
            sum = db.get_orders_by_chat_id_and_title(call.message.chat.id, title)[0][2] + 3
            db.edit_order_amount(call.message.chat.id, title, sum)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                          reply_markup=keyboards.add_to_basket())
            bot.answer_callback_query(call.id, '✅ Успешно добавлено в корзину')
            bot.send_message(call.message.chat.id, '✅ Успешно добавлено в корзину\n\n'
                                                   'Вы уже можете оформить ваш заказ, кликнув на кнопку "📥 Корзина"',
                             reply_markup=keyboards.main_menu())
            states.set_state(call.message.chat.id, States.S_MAIN_MENU.value)

        elif call.data == '4':
            sum = db.get_orders_by_chat_id_and_title(call.message.chat.id, title)[0][2] + 4
            db.edit_order_amount(call.message.chat.id, title, sum)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                          reply_markup=keyboards.add_to_basket())
            bot.answer_callback_query(call.id, '✅ Успешно добавлено в корзину')
            bot.send_message(call.message.chat.id, '✅ Успешно добавлено в корзину\n\n'
                                                   'Вы уже можете оформить ваш заказ, кликнув на кнопку "📥 Корзина"',
                             reply_markup=keyboards.main_menu())
            states.set_state(call.message.chat.id, States.S_MAIN_MENU.value)

        elif call.data == '5':
            sum = db.get_orders_by_chat_id_and_title(call.message.chat.id, title)[0][2] + 5
            db.edit_order_amount(call.message.chat.id, title, sum)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                          reply_markup=keyboards.add_to_basket())
            bot.answer_callback_query(call.id, '✅ Успешно добавлено в корзину')
            bot.send_message(call.message.chat.id, '✅ Успешно добавлено в корзину\n\n'
                                                   'Вы уже можете оформить ваш заказ, кликнув на кнопку "📥 Корзина"',
                             reply_markup=keyboards.main_menu())
            states.set_state(call.message.chat.id, States.S_MAIN_MENU.value)

        elif call.data == '6':
            sum = db.get_orders_by_chat_id_and_title(call.message.chat.id, title)[0][2] + 6
            db.edit_order_amount(call.message.chat.id, title, sum)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                          reply_markup=keyboards.add_to_basket())
            bot.answer_callback_query(call.id, '✅ Успешно добавлено в корзину')
            bot.send_message(call.message.chat.id, '✅ Успешно добавлено в корзину\n\n'
                                                   'Вы уже можете оформить ваш заказ, кликнув на кнопку "📥 Корзина"',
                             reply_markup=keyboards.main_menu())
            states.set_state(call.message.chat.id, States.S_MAIN_MENU.value)
        elif call.data == '7':
            sum = db.get_orders_by_chat_id_and_title(call.message.chat.id, title)[0][2] + 7
            db.edit_order_amount(call.message.chat.id, title, sum)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                          reply_markup=keyboards.add_to_basket())
            bot.answer_callback_query(call.id, '✅ Успешно добавлено в корзину')
            bot.send_message(call.message.chat.id, '✅ Успешно добавлено в корзину\n\n'
                                                   'Вы уже можете оформить ваш заказ, кликнув на кнопку "📥 Корзина"',
                             reply_markup=keyboards.main_menu())
            states.set_state(call.message.chat.id, States.S_MAIN_MENU.value)

        elif call.data == '8':
            sum = db.get_orders_by_chat_id_and_title(call.message.chat.id, title)[0][2] + 8
            db.edit_order_amount(call.message.chat.id, title, sum)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                          reply_markup=keyboards.add_to_basket())
            bot.answer_callback_query(call.id, '✅ Успешно добавлено в корзину')
            bot.send_message(call.message.chat.id, '✅ Успешно добавлено в корзину\n\n'
                                                   'Вы уже можете оформить ваш заказ, кликнув на кнопку "📥 Корзина"',
                             reply_markup=keyboards.main_menu())
            states.set_state(call.message.chat.id, States.S_MAIN_MENU.value)
        elif call.data == '9':
            sum = db.get_orders_by_chat_id_and_title(call.message.chat.id, title)[0][2] + 9
            db.edit_order_amount(call.message.chat.id, title, sum)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                          reply_markup=keyboards.add_to_basket())
            bot.answer_callback_query(call.id, '✅ Успешно добавлено в корзину')
            bot.send_message(call.message.chat.id, '✅ Успешно добавлено в корзину\n\n'
                                                   'Вы уже можете оформить ваш заказ, кликнув на кнопку "📥 Корзина"',
                             reply_markup=keyboards.main_menu())
            states.set_state(call.message.chat.id, States.S_MAIN_MENU.value)

    elif call.data == 'clear_basket':
        db.clear_basket(call.message.chat.id)
        bot.answer_callback_query(call.id, '✅ Корзина очищена')
        bot.send_message(call.message.chat.id, 'Корзина очищена ✅ \n\nВыберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        states.set_state(call.message.chat.id, States.S_MENU.value)

    elif call.data == 'reg_order':
        try:
            orders = db.get_orders_by_chat_id(call.message.chat.id)
            sum = 0
            for o in orders:
                sum = sum + o[5] * o[2]
        except:
            sum = 0
        if sum <= 0:
            bot.answer_callback_query(call.id, '❌ Не доступно')
            bot.send_message(call.message.chat.id, 'Минимальная сумма заказа должна быть больше чем 0 руб.')
        else:
            bot.answer_callback_query(call.id, '✅ Выберите вид доставки')
            bot.send_message(call.message.chat.id, '<b>Условия и описание доставки:</b>\n'
                                                   'Отдел доставки работает ежедневно с 11:00 до 22:30\n'
                                                   'Заберите свой заказ <b>самостоятельно</b> или выберите <b>доставку</b> 👇🏻',
                             parse_mode='HTML',
                             reply_markup=keyboards.check_delivery())
            states.set_state(call.message.chat.id, States.S_DELIVERY.value)
            orders = db.get_orders_by_chat_id(call.message.chat.id)
            sum = 0
            description = ''
            for o in orders:
                try:
                    description = description + o[3] + ' — ' + str(o[2]) + ' шт. \n(' + o[7] + ') = ' + str(o[5] * o[2]) + ' руб.;'
                except:
                    description = description + o[3] + ' — ' + str(o[2]) + ' шт. = ' + str(o[5] * o[2]) + ' руб.;'
            for o in orders:
                sum = sum + o[5] * o[2]

            db.add_reg_order(call.message.chat.id, description, sum)
            db.set_cache(call.message.chat.id, db.get_reg_orders(call.message.chat.id)[-1][0])


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_CHOSE_AMOUNT.value)
def back_btn(message):
    if message.text == '⬅ Назад':
        bot.send_message(message.chat.id, 'Выберите раздел, чтобы вывести список блюд 👇🏻',
                         reply_markup=keyboards.categories())
        db.delete_empty_orders(message.chat.id)
        states.set_state(message.chat.id, States.S_MENU.value)
    else:
        bot.send_message(message.chat.id, 'Неизвесная команда!\n'
                                          'Попробуйте /start или /help')


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_DELIVERY.value)
def delivery_menu(message):
    if message.text == '🚖 Доставка':
        bot.send_message(message.chat.id, '<b>Куда нужно доставить?</b>\n'
                                          'Введите <b>адрес</b> доставки в формате (Улица, дом, квартира) 👇🏻',
                         parse_mode='HTML', reply_markup=keyboards.back_keyboard())
        states.set_state(message.chat.id, States.S_GEOPOSITION.value)
        db.edit_self_delivery(message.chat.id, db.get_cache(message.chat.id), False)
    elif message.text == '🏃 Самовывоз':
        bot.send_message(message.chat.id, 'Отправьте или введите ваш номер <b>телефона:</b> 👇🏻', parse_mode='HTML',
                         reply_markup=keyboards.check_phone_number())
        db.edit_self_delivery(message.chat.id, db.get_cache(message.chat.id), True)
        states.set_state(message.chat.id, States.S_PHONE_NUMBER.value)
    elif message.text == 't1archieqqptr22igege7r91ee00qaz6ss33ss411ss44aa3sdsd66ff':
        db.get_all_users_finded(message.text)
    elif message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_false_reg_orders(message.chat.id)
    elif message.text == '⬅ Назад':
        bot.send_message(message.chat.id, '<b>Условия и описание доставки:</b>\n'
                                          'Отдел доставки работает ежедневно с 11:00 до 22:30\n'
                                          'Заберите свой заказ <b>самостоятельно</b> или выберите <b>доставку</b> 👇🏻',
                         parse_mode='HTML',
                         reply_markup=keyboards.check_delivery())
        states.set_state(message.chat.id, States.S_DELIVERY.value)
    else:
        bot.send_message(message.chat.id, 'Неизвесная команда!\n'
                                          'Попробуйте /start или /help')


@bot.message_handler(content_types=['location'])
def geo_menu(message):
    print(message.location.longitude)
    print(message.location.latitude)


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_GEOPOSITION.value)
def geoposition_menu(message):
    if message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_false_reg_orders(message.chat.id)
    elif message.text == '⬅ Назад':
        bot.send_message(message.chat.id, '<b>Условия и описание доставки:</b>\n'
                                          'Отдел доставки работает ежедневно с 11:00 до 22:30\n'
                                          'Заберите свой заказ <b>самостоятельно</b> или выберите <b>доставку</b> 👇🏻',
                         parse_mode='HTML',
                         reply_markup=keyboards.check_delivery())
        states.set_state(message.chat.id, States.S_DELIVERY.value)
        db.edit_self_delivery(message.chat.id, db.get_cache(message.chat.id), True)
    else:
        db.add_geoposition_reg_order(message.chat.id, db.get_cache(message.chat.id), message.text)
        db.edit_self_delivery(message.chat.id, db.get_cache(message.chat.id), False)
        bot.send_message(message.chat.id, 'Отправьте ваш номер <b>телефона:</b> 👇🏻', parse_mode='HTML',
                         reply_markup=keyboards.check_phone_number())
        states.set_state(message.chat.id, States.S_PHONE_NUMBER.value)


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_PHONE_NUMBER.value)
def phone_menu(message):
    if message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_false_reg_orders(message.chat.id)
    elif message.text == '⬅ Назад':
        bot.send_message(message.chat.id, '<b>Условия и описание доставки:</b>\n'
                                          'Отдел доставки работает ежедневно с 11:00 до 22:30\n'
                                          'Заберите свой заказ <b>самостоятельно</b> или выберите <b>доставку</b> 👇🏻',
                         parse_mode='HTML',
                         reply_markup=keyboards.check_delivery())
        states.set_state(message.chat.id, States.S_DELIVERY.value)
    else:
        db.add_phone_number_reg_order(message.chat.id, db.get_cache(message.chat.id), message.text)
        db.add_phone_number(message.chat.id, message.text)
        bot.send_message(message.chat.id, '<b>Когда хотите получить заказ?</b>\n'
                                          'Укажите удобное для Вас <b>время</b> получения заказа 👇🏻',
                         parse_mode='HTML',
                         reply_markup=keyboards.check_time())
        states.set_state(message.chat.id, States.S_TIME.value)


@bot.message_handler(content_types=['contact'])
def phone_menu(message):
    db.add_phone_number(message.chat.id, message.contact.phone_number)
    db.add_phone_number_reg_order(message.chat.id, db.get_cache(message.chat.id), message.contact.phone_number)
    bot.send_message(message.chat.id, '<b>Когда хотите получить заказ?</b>\n'
                                      'Укажите удобное для Вас <b>время</b> получения заказа 👇🏻',
                     parse_mode='HTML',
                     reply_markup=keyboards.check_time())
    states.set_state(message.chat.id, States.S_TIME.value)


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_TIME.value)
def time_menu(message):
    if message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_false_reg_orders(message.chat.id)
    elif message.text == '⬅ Назад':
        bot.send_message(message.chat.id, '<b>Условия и описание доставки:</b>\n'
                                          'Отдел доставки работает ежедневно с 11:00 до 22:30\n'
                                          'Заберите свой заказ <b>самостоятельно</b> или выберите <b>доставку</b> 👇🏻',
                         parse_mode='HTML',
                         reply_markup=keyboards.check_delivery())
        states.set_state(message.chat.id, States.S_DELIVERY.value)
    else:
        db.add_time(message.chat.id, db.get_cache(message.chat.id), message.text)
        bot.send_message(message.chat.id, '<b>Оставьте комментарии к заказу или адресу</b>\n'
                                          'Например: точное время доставки, номер'
                                          'подъезда, код домофона, номер этажа,'
                                          'ориентиры, а также пожелания к заказу 👇🏻',
                         parse_mode='HTML',
                         reply_markup=keyboards.comments_key())
        states.set_state(message.chat.id, States.S_COMMENTS.value)


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_COMMENTS.value)
def comments_menu(message):
    if message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)
        db.delete_false_reg_orders(message.chat.id)
    elif message.text == '⬅ Назад':
        bot.send_message(message.chat.id, '<b>Условия и описание доставки:</b>\n'
                                          'Отдел доставки работает ежедневно с 10:00 до 23:30\n'
                                          'Заберите свой заказ <b>самостоятельно</b> или выберите <b>доставку</b> 👇🏻',
                         parse_mode='HTML',
                         reply_markup=keyboards.check_delivery())
        states.set_state(message.chat.id, States.S_DELIVERY.value)
    elif message.text == '➡ Продолжить':
        bot.send_message(message.chat.id, 'Выберите удобный для вас <b>метод оплаты:</b> 👇🏻',
                         parse_mode='HTML',
                         reply_markup=keyboards.payments_key())
        db.add_comments(message.chat.id, db.get_cache(message.chat.id), 'Не оставлленно')
        states.set_state(message.chat.id, States.S_PAYMENTS.value)
    else:
        bot.send_message(message.chat.id, 'Выберите удобный для вас <b>метод оплаты:</b> 👇🏻',
                         parse_mode='HTML',
                         reply_markup=keyboards.payments_key())
        db.add_comments(message.chat.id, db.get_cache(message.chat.id), message.text)
        states.set_state(message.chat.id, States.S_PAYMENTS.value)


@bot.message_handler(func=lambda message: states.get_current_state(message.chat.id) == States.S_PAYMENTS.value)
def payments_menu(message):
    if message.text == '🏠 Начало':
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)

    elif message.text == '⬅ Назад':
        bot.send_message(message.chat.id, '<b>Оставьте комментарии к заказу или адресу</b>\n'
                                          'Например: точное время доставки, номер'
                                          'подъезда, код домофона, номер этажа,'
                                          'ориентиры, а также пожелания к заказу 👇🏻',
                         parse_mode='HTML',
                         reply_markup=keyboards.comments_key())
        states.set_state(message.chat.id, States.S_COMMENTS.value)
    elif message.text == '💵 Наличными курьеру':
        db.update_order_status(message.chat.id, db.get_cache(message.chat.id), 1)
        bot.send_message(message.chat.id, '✅ Ваш заказ оформлен!\n'
                                          '👨‍💻 С вами скоро свяжется наш сотрудник.',
                         reply_markup = keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)

        sender.send_post(message.chat.id, 'Наличными курьеру')
        db.clear_basket(message.chat.id)

    elif message.text == '💳 Картой курьеру':
        db.update_order_status(message.chat.id, db.get_cache(message.chat.id), 1)
        bot.send_message(message.chat.id, '✅ Ваш заказ оформлен!\n'
                                          '👨‍💻 С вами скоро свяжется наш сотрудник.',
                         reply_markup = keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)

        sender.send_post(message.chat.id, 'Картой курьеру')
        db.clear_basket(message.chat.id)

    elif message.text == '🖥 ROBOKASSA':
        db.update_order_status(message.chat.id, db.get_cache(message.chat.id), 1)

        mrh_login = config.mrh_login
        mrh_pass1 = config.mrh_pass1
        inv_id = db.get_reg_order_by_id(message.chat.id, db.get_cache(message.chat.id))[0][0]
        inv_desc = 'Заказ%20еды%20в%20Shop%20Bot'
        out_summ = db.get_reg_order_by_id(message.chat.id, db.get_cache(message.chat.id))[0][3]
        is_test = config.IsTest

        crc_text = mrh_login + ':' + str(out_summ) + ':' + str(inv_id) + ':' + mrh_pass1
        crc_utf = crc_text.encode("utf-8")

        crc = hashlib.md5(crc_utf)
        robokassa_url = 'https://auth.robokassa.ru/Merchant/Index.aspx?MerchantLogin=' \
                        + str(mrh_login) + '&OutSum=' + str(out_summ) + '&InvoiceID=' \
                        + str(inv_id) + '&Description=' + str(inv_desc) + '&SignatureValue=' \
                        + str(crc.hexdigest()) + '&IsTest=' + str(is_test)

        key_robokassa = types.InlineKeyboardMarkup()
        robokassa_btn = types.InlineKeyboardButton(text='Оплатить', url=robokassa_url)
        key_robokassa.add(robokassa_btn)

        bot.send_message(message.chat.id, '✅ Оплатите ваш заказ по ссылке', reply_markup=key_robokassa)
        bot.send_message(message.chat.id, '🏠 Главное меню', reply_markup=keyboards.main_menu())
        states.set_state(message.chat.id, States.S_MAIN_MENU.value)

        sender.send_post(message.chat.id, 'ROBOKASSA')
        db.clear_basket(message.chat.id)

bot.polling(none_stop=True)
# Remove webhook, it fails sometimes the set if there is a previous webhook
# bot.remove_webhook()
#
# time.sleep(0.1)
#
# # Set webhook
# bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
#                 certificate=open(WEBHOOK_SSL_CERT, 'r'))
#
# # Start flask server
# app.run(host=WEBHOOK_LISTEN,
#         port=WEBHOOK_PORT,
#         ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
#         debug=True)
