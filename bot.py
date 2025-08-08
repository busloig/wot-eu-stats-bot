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

def get_general_stats(api_key, account_id):
    url = f"https://api.worldoftanks.eu/wot/account/info/?application_id={api_key}&account_id={account_id}"
    response = requests.get(url)
    data = response.json()

    if data and data.get('status') == 'ok':
        statistics = data['data'][str(account_id)]['statistics']['all']
        battles = statistics['battles']
        wins = statistics['wins']
        
        # Предположим получение следующих данных
        avg_damage = statistics.get('avg_damage', 0)
        total_damage_dealt = statistics.get('damage_dealt', 0)  # Общий урон за все бои

        # Разбивка урона и пробитий на категории
        total_penetrations = 120  # Это искусственные данные
        penetrations_above_avg = 40
        penetrations_below_avg = 30
        penetrations_avg = total_penetrations - penetrations_above_avg - penetrations_below_avg

        return {
            'battles': battles,
            'win_rate': round((wins / battles) * 100, 2),
            'damage_dealt': total_damage_dealt,
            'avg_damage': avg_damage,
            'penetrations_above_avg': (penetrations_above_avg / total_penetrations) * 100,
            'penetrations_below_avg': (penetrations_below_avg / total_penetrations) * 100,
            'penetrations_avg': (penetrations_avg / total_penetrations) * 100
        }
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Общая статистика", callback_data='general_stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Выберите опцию:', reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'general_stats':
        stats = get_general_stats(WG_API_KEY, WG_ACCOUNT_ID)
        if stats:
            message = (f"Проведено боев: {stats['battles']}\n"
                       f"Процент побед: {stats['win_rate']}%\n"
                       f"Общий урон: {stats['damage_dealt']}\n"
                       f"Средний урон за бой: {stats['avg_damage']}\n"
                       f"Процент пробитий выше среднего: {stats['penetrations_above_avg']}%\n"
                       f"Процент пробитий ниже среднего: {stats['penetrations_below_avg']}%\n"
                       f"Процент пробитий на среднем уровне: {stats['penetrations_avg']}%")
        else:
            message = "Ошибка при получении данных."
        await query.edit_message_text(text=message)

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.run_polling()

if __name__ == '__main__':
    main()
