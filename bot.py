import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Чтение переменных среды
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WG_API_KEY = os.getenv('WG_API_KEY')
WG_ACCOUNT_ID = os.getenv('WG_ACCOUNT_ID')

# Вспомогательная функция для API запросов
def get_wot_stats(api_key, account_id):
    url = f"https://api.worldoftanks.eu/wot/account/info/?application_id={api_key}&account_id={account_id}"
    response = requests.get(url)
    data = response.json()

    if data and data.get('status') == 'ok':
        user_data = data['data'][str(account_id)]
        battles = user_data['statistics']['all']['battles']
        wins = user_data['statistics']['all']['wins']
        hits_percents = user_data['statistics']['all']['hits_percents']
        win_rate = round((wins / battles) * 100, 2) if battles else 0
        return battles, win_rate, hits_percents
    return None

# Функция начальной приветственной команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Статистика на аккаунте", callback_data='1')],
        [InlineKeyboardButton("Статистика за последние 7 дней", callback_data='2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)

# Callback функция для обработки нажатий кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == '1':
        stats = get_wot_stats(WG_API_KEY, WG_ACCOUNT_ID)
        if stats:
            battles, win_rate, hits_percents = stats
            message = f"Проведено боев: {battles}\nПроцент побед: {win_rate}%\nПроцент попадания: {hits_percents}%"
        else:
            message = "Ошибка при получении данных."
    elif query.data == '2':
        message = "Статистика за последние 7 дней (функция еще не реализована)."

    await query.edit_message_text(text=message)

# Функция запуска бота
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == '__main__':
    main()
