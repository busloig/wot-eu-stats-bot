import os
import requests
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Чтение переменных среды
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WG_API_KEY = os.getenv('WG_API_KEY')
WG_ACCOUNT_ID = os.getenv('WG_ACCOUNT_ID')

# Функция для получения общей статистики из WoT API
def get_general_stats(api_key, account_id):
    url = f"https://api.worldoftanks.eu/wot/account/info/?application_id={api_key}&account_id={account_id}"
    response = requests.get(url)
    data = response.json()

    if data and data.get('status') == 'ok':
        statistics = data['data'][str(account_id)]['statistics']['all']
        battles = statistics['battles']
        wins = statistics['wins']
        
        # Данные по урону
        avg_damage = statistics.get('avg_damage', 0)
        damage_above_avg = 75  # Пример данных
        damage_below_avg = 50  # Пример данных
        
        # Данные по пробитию
        avg_penetrations = statistics.get('avg_penetrations', 0)
        penetrations_above_avg = 40
        penetrations_below_avg = 30

        return {
            'battles': battles,
            'win_rate': round((wins / battles) * 100, 2),
            'damage_above_avg': round((damage_above_avg / battles) * 100, 2),
            'damage_below_avg': round((damage_below_avg / battles) * 100, 2),
            'damage_avg': round((battles - damage_above_avg - damage_below_avg) * 100 / battles, 2),
            'penetrations_above_avg': round((penetrations_above_avg / battles) * 100, 2),
            'penetrations_below_avg': round((penetrations_below_avg / battles) * 100, 2),
            'penetrations_avg': round((battles - penetrations_above_avg - penetrations_below_avg) * 100 / battles, 2)
        }
    return None

# Функция обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Общая статистика", callback_data='general_stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)

# Функция для обработки кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'general_stats':
        stats = get_general_stats(WG_API_KEY, WG_ACCOUNT_ID)
        if stats:
            message = (f"Проведено боев: {stats['battles']}\n"
                       f"Процент побед: {stats['win_rate']}%\n"
                       f"Урон выше среднего: {stats['damage_above_avg']}%\n"
                       f"Урон ниже среднего: {stats['damage_below_avg']}%\n"
                       f"Средний урон: {stats['damage_avg']}%\n"
                       f"Пробития выше среднего: {stats['penetrations_above_avg']}%\n"
                       f"Пробития ниже среднего: {stats['penetrations_below_avg']}%\n"
                       f"Средние пробития: {stats['penetrations_avg']}%")
        else:
            message = "Ошибка при получении данных."
        await query.edit_message_text(text=message)

# Основная функция запуска бота
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == '__main__':
    main()
