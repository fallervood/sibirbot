import os
import telebot
from telebot import types

# Bot's API Token
bot = telebot.TeleBot('1764992375:AAEMv-RluXiYb5bJBbyiyhc-wfauGMCQzPU')
# Variables
post = ''
author = ''
admin_id = ''
admin_checker = False
password = '421'
image = None
start_message = 'Привет! Хочешь написать пост?'
change_start_message = False


# -- Commands handler --
@bot.message_handler(commands=['start', 'admin'])
def get_command_messages(message):
	# Start
	if message.text == "/start":
		bot.send_message(message.chat.id, start_message, reply_markup=keyboard_menu())
	if message.text == "/admin":
		global admin_checker
		bot.send_message(message.from_user.id, "Введите пароль 🔐")
		admin_checker = True


# -- Messages Handler --
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
	global post
	global author
	global admin_checker
	global admin_id
	global start_message
	global change_start_message

	# Some text
	if message.text == password and admin_checker:
		bot.send_message(message.chat.id, "Новый id админа успешно установлен! 🔓", reply_markup=keyboard_admin())
		admin_id = message.from_user.id
		admin_checker = False
		print("Новый админ:", message.from_user.id)
	elif message.text != password and admin_checker:
		bot.send_message(message.chat.id, "Пароль неверный! 🔒")
		admin_checker = False
		print("Зафиксирована попытка входа в админку, от пользователя:", message.from_user.username, message.from_user.id)
	elif change_start_message and message.from_user.id == admin_id:
		start_message = message.text
		bot.send_message(admin_id, "Приветствие успешно измененно!", reply_markup=keyboard_admin())
		change_start_message = False
	elif message.from_user.id == admin_id and message.text == "Поменять_приветствие":
		bot.send_message(admin_id, "Введите приветствие")
		change_start_message = True
	else:
		post = message.text
		author = message.chat.username
		bot.send_message(message.chat.id, f"*Новый пост:*\n{post} \n*Автор:* {author}\n*Прикрепленный файл:* ⏬", parse_mode="Markdown")
		if image != None: bot.send_photo(message.chat.id, image)
		else: bot.send_message(message.chat.id, "_Вы ничего не отправили_", parse_mode="Markdown")
		bot.send_message(message.chat.id, "Отправить?", reply_markup=keyboard_create())


# -- Content Handler --
@bot.message_handler(content_types=['photo'])
def get_photo_messages(message):
	global image
	global author
	file_info = bot.get_file(message.photo[len(message.photo)-1].file_id)
	file_name, file_extension = os.path.splitext(file_info.file_path)
	src = file_name + file_extension
	image = file_info.file_id
	author = message.chat.username
	bot.send_message(message.chat.id, f"*Новый пост:*\n{post} \n*Автор:* {author}\n*Прикрепленный файл:* ⏬", parse_mode="Markdown")
	bot.send_photo(message.chat.id, image)
	bot.send_message(message.chat.id, "Отправить?", reply_markup=keyboard_create())


# -- Callback --
@bot.callback_query_handler(func=lambda call: True)
def get_callback(call):
	global post
	global author
	global image
	if call.data == "new_post":
		bot.send_message(call.message.chat.id, 'Отправьте пост после этого сообщения ⏬')
	if call.data == "info":
		bot.send_message(call.message.chat.id, '''
Вы можете написать боту любой текст после чего он предложит отправить это на проверку админу, расценивая это как пост. \n
Если Вы хотите разместить картинку, просто отправьте его после поста.\n
Если Вы хотите оставить ссылку на файл - отправьте ее вместе с постом.\n
Если Вы хотите написать пост снова не отправляя черновик - нажмите "Отмена".\n

-------------Временная информация-------------------
**Текст** – комбинация делает шрифт жирным.\n
__Текст__ – комбинация наклоняет шрифт.''')
	if call.data == "send_post":
		try:
			get_new_post(post, author, image)
			bot.send_message(call.message.chat.id, 'Ваш пост успешно отправлен и будет опубликован после проверки! ✅')
			post = ''
			author = ''
			image = None
		except:
			bot.send_message(call.message.chat.id, 'К сожалению сейчас нет админа!')
	if call.data == "send_img":
		bot.send_message(call.message.chat.id, 'Пришлите файл. 📄\nМожно прикрепить только 1 файл')
	if call.data == "cancel_post":
		post = ''
		author = ''
		image = None
		bot.send_message(call.message.chat.id, 'Пост успешно удален!')


# -- Sending Post --
def get_new_post(text, user, image=None):
	global admin_id
	bot.send_message(admin_id, f"*Новый пост:*\n{text} \n*Автор:* {user}\n*Прикрепленный файл:* ⏬", parse_mode="Markdown")
	if image != None: bot.send_photo(admin_id, image)
	else: bot.send_message(admin_id, "Ничего не прикрепили")


# -- Keyboards --
def keyboard_menu():
	markup = types.InlineKeyboardMarkup()
	button_nav = types.InlineKeyboardButton("Написать пост 📝", callback_data='new_post')
	button_check = types.InlineKeyboardButton("Подробнее 🔍", callback_data='info')
	markup.add(button_nav, button_check)
	return markup


def keyboard_create():
	markup = types.InlineKeyboardMarkup()
	button_done = types.InlineKeyboardButton("Отправить ✉", callback_data='send_post')
	button_img = types.InlineKeyboardButton("Прикрепить фото 📎", callback_data='send_img')
	button_cancel = types.InlineKeyboardButton("Отмена 🚫", callback_data='cancel_post')
	markup.add(button_done, button_img)
	markup.add(button_cancel)
	return markup


def keyboard_admin():
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
	button_change_start_message = types.KeyboardButton("Поменять_приветствие")
	markup.add(button_change_start_message)
	return markup


# -- Polling --
bot.polling(none_stop=False, interval=0, timeout=20)