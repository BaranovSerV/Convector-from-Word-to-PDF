import telebot
import openai

# Токен вашего бота, который вы получили от BotFather в Telegram
TOKEN = '6718122659:AAETeWZjwaEa6d5stXF_tNUwqSuWNA4A6bo'


bot = telebot.TeleBot(TOKEN)

# Установка ключа API для доступа к OpenAI GPT-3
openai.api_key = 'Ysk-proj-r0RIAVkHFByoLovaX9HlT3BlbkFJWndAVkiR8CQzO2lH2XMe'

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Я ChatGPT бот. Отправь мне сообщение, и я сгенерирую текст на основе вашего ввода.")

# Обработчик входящих сообщений
@bot.message_handler(func=lambda message: True)
def generate_text(message):
    user_input = message.text
    # Генерация ответа от модели ChatGPT
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=user_input,
        max_tokens=50
    )
    bot.send_message(message.chat.id, response.choices[0].text.strip())

# Запуск бота
bot.polling()
