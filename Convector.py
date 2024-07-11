import telebot
from telebot import types
import base64
import requests
import time

API_TOKEN = 'Your API TOKEN'
CONVERTIO_API_KEY = 'Your API KEY'
CONVERTIO_API_URL = 'https://api.convertio.co/convert'

admins = [] # administrator's ID

bot = telebot.TeleBot(API_TOKEN)

"""Работа конвектора PDF"""
@bot.message_handler(commands=['start'])
def ask_for_document(message):
    bot.reply_to(message, "Отправь мне файл в формате Word, и я конвертирую его в PDF.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        file_id = message.document.file_id
        file_info = bot.get_file(file_id)
        file_path = file_info.file_path
        file_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"

        # Загрузка файла с сервера Telegram
        file_content = requests.get(file_url).content

        # Подготовка данных для загрузки на Convertio
        payload = {
            'apikey': CONVERTIO_API_KEY,
            'input': 'base64',
            'file': base64.b64encode(file_content).decode('utf-8'),
            'filename': message.document.file_name,
            'outputformat': 'pdf'
        }

        # Загрузка файла на Convertio
        response = requests.post(CONVERTIO_API_URL, json=payload)
        conversion_data = response.json()

        if conversion_data['status'] == 'ok':
            conversion_id = conversion_data['data']['id']
            bot.reply_to(message, f"Файл загружен...")

            # Ожидание завершения конвертации
            while True:
                status_response = requests.get(f"{CONVERTIO_API_URL}/{conversion_id}/status")
                status_data = status_response.json()

                if status_data['status'] != 'ok':
                    bot.reply_to(message, f"Ошибка при проверке статуса: {status_data}")
                    return

                if status_data['data']['step'] == 'finish':
                    break
                time.sleep(3)

            # Получение ссылки на конвертированный файл
            result_url = status_data['data']['output']['url']

            # Вывод отладочной информации
            #bot.reply_to(message, f"Отладочная информация: {json.dumps(status_data, indent=2)}")

            # Скачивание конвертированного файла и отправка пользователю
            pdf_content = requests.get(result_url).content
            bot.send_document(message.chat.id, (f"{message.document.file_name.split('.')[0]}.pdf", pdf_content))
        else:
            send_long_message(message.chat.id, f"Ошибка при конвертации: {conversion_data['error']}")
    except Exception as e:
        send_long_message(message.chat.id, f"Произошла ошибка: {str(e)}")

def send_long_message(chat_id, text):
    """Разбивает длинное сообщение на несколько более коротких и отправляет их по отдельности."""
    max_length = 4096  # Максимальная длина сообщения в Telegram
    for i in range(0, len(text), max_length):
        bot.send_message(chat_id, text[i:i+max_length])

# Запускаем бота
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        for admin_id in admins:
            error_bot = f'''{str(e)}'''
            formatted_code = f"<pre><code>{error_bot}</code></pre>"
            bot.send_message(admin_id, f"Ошибка при запуске бота:{formatted_code}", parse_mode='HTML')
        time.sleep(5)  # Перезапускаем бота через 5 секунд, если произошла ошибка
