import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для получения статистики из API Wargaming
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

# Обработчик команды /stats
async def wot_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_key = 'YOUR_WG_API_KEY'
    account_id = 'YOUR_ACCOUNT_ID'
    stats = get_wot_stats(api_key, account_id)
    if stats:
        battles, win_rate, hits_percents = stats
        message = f"Проведено боев: {battles}\nПроцент побед: {win_rate}%\nПроцент попадания: {hits_percents}%"
    else:
        message = "Ошибка при получении данных."
    await update.message.reply_text(message)

# Функция запуска бота
def main():
    application = Application.builder().token('YOUR_TELEGRAM_BOT_TOKEN').build()
    application.add_handler(CommandHandler('stats', wot_stats))
    application.run_polling()

if __name__ == '__main__':
    main()
