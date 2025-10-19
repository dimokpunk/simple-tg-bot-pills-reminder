import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import schedule
import time
import random
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Настройка прокси для PythonAnywhere
os.environ["HTTPS_PROXY"] = "http://proxy.server:3128"

# Настройки
TOKEN = "8309621303:AAFpBlDwyrTaoZFEtHtxSYuyrVXszH9B-0Q"
ADMIN_CHAT_ID = 1185667911  # Ваш chat_id, добавьте после теста
CHAT_IDS = set()  # Множество для хранения chat_id всех пользователей

# Список из 30 статических картинок по теме "Здоровье" с Unsplash
HEALTH_IMAGES = [
    "https://images.unsplash.com/photo-1506126613408-eca37b8d7a2d",
    "https://images.unsplash.com/photo-1540497077202-7c8a3999166f",
    "https://images.unsplash.com/photo-1512621776951-a57141f2eefd",
    "https://images.unsplash.com/photo-1498837167922-ddd27525d352",
    "https://images.unsplash.com/photo-1517430816045-df4b7de11d1d",
    "https://images.unsplash.com/photo-1507226988209-1b7590f7d6a7",
    "https://images.unsplash.com/photo-1518611012118-69688d064911",
    "https://images.unsplash.com/photo-1544367567-0f2fcb009655",
    "https://images.unsplash.com/photo-1505751172876-fa1923c5c7a2",
    "https://images.unsplash.com/photo-1515377905703-c4788e51af15",
    "https://images.unsplash.com/photo-1522898467493-49726bf28798",
    "https://images.unsplash.com/photo-1494599948593-3da3d82e5902",
    "https://images.unsplash.com/photo-1532938911079-1b3550d97e26",
    "https://images.unsplash.com/photo-1505576391880-b3f9d71385cb",
    "https://images.unsplash.com/photo-1543353071-873f17a7a088",
    "https://images.unsplash.com/photo-1506459225024-8f6738c9ef73",
    "https://images.unsplash.com/photo-1504813184591-01572f98c85f",
    "https://images.unsplash.com/photo-1490818387583-1c64a8f31b4f",
    "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2",
    "https://images.unsplash.com/photo-1506521781261-d73408351382",
    "https://images.unsplash.com/photo-1517832207067-4db24a2ae47c",
    "https://images.unsplash.com/photo-1541623088465-0c7c4f4b24e4",
    "https://images.unsplash.com/photo-1518310383032-8204a6ab07fa",
    "https://images.unsplash.com/photo-1507048331197-7d4ac70811cf",
    "https://images.unsplash.com/photo-1519681393784-d120267933ba",
    "https://images.unsplash.com/photo-1518609878373-06d740f60d8b",
    "https://images.unsplash.com/photo-1528715471579-eb29c3d01b03",
    "https://images.unsplash.com/photo-1517433367423-79d631011783",
    "https://images.unsplash.com/photo-1506126279646-1db9f1b4b7a0",
    "https://images.unsplash.com/photo-1515378960530-7c0da6231fb1"
]

# Инициализация бота с таймаутами
bot = telegram.Bot(token=TOKEN, request=telegram.utils.request.Request(con_pool_size=8, connect_timeout=10.0, read_timeout=30.0))

# Напоминание о таблетке
def send_pill_reminder():
    if not CHAT_IDS:
        print("Нет активных пользователей для напоминаний.")
        return
    message = "Не забудь выпить таблетки! Будь здоров! 😊"
    image = random.choice(HEALTH_IMAGES)  # Случайная картинка
    keyboard = [[InlineKeyboardButton("Таблетки выпил! ✅", callback_data="pill_taken")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    for chat_id in CHAT_IDS:
        try:
            bot.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)
            bot.send_photo(chat_id=chat_id, photo=image)
            print(f"Напоминание отправлено для chat_id {chat_id} в {datetime.now()} (UTC)")
        except Exception as e:
            print(f"Ошибка при отправке напоминания для chat_id {chat_id}: {e}")
            if ADMIN_CHAT_ID:
                bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Ошибка для chat_id {chat_id}: {str(e)}")

# Напоминание о здоровье в 12:00 (+4)
def send_health_reminder():
    if not CHAT_IDS:
        print("Нет активных пользователей для напоминаний о здоровье.")
        return
    message = "Не забывай думать о своём здоровье! Твои дети и внуки хотят чтобы ты был с ними рядом как можно дольше, в добром здравии."
    for chat_id in CHAT_IDS:
        try:
            bot.send_message(chat_id=chat_id, text=message)
            print(f"Напоминание о здоровье отправлено для chat_id {chat_id} в {datetime.now()} (UTC)")
        except Exception as e:
            print(f"Ошибка при отправке напоминания о здоровье для chat_id {chat_id}: {e}")
            if ADMIN_CHAT_ID:
                bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Ошибка для chat_id {chat_id}: {str(e)}")

# Команда /test
def test(update, context):
    if not CHAT_IDS:
        update.message.reply_text("Бот активен, но ты не подписан на напоминания. Используй /start.")
        return
    # Временные метки напоминаний в UTC (+4 UTC: 6:00→2:00, 12:00→8:00, 20:00→16:00)
    now = datetime.now(ZoneInfo("UTC"))
    today = now.date()
    reminder_times = [
        datetime(today.year, today.month, today.day, 2, 0, tzinfo=ZoneInfo("UTC")),  # 6:00 +4
        datetime(today.year, today.month, today.day, 8, 0, tzinfo=ZoneInfo("UTC")),  # 12:00 +4
        datetime(today.year, today.month, today.day, 16, 0, tzinfo=ZoneInfo("UTC"))  # 20:00 +4
    ]
    # Если время прошло, добавляем на следующий день
    next_day_reminders = [
        t + timedelta(days=1) for t in reminder_times if t <= now
    ]
    reminder_times.extend(next_day_reminders)
    # Находим ближайшее будущее время
    next_reminder = min(t for t in reminder_times if t > now)
    time_diff = next_reminder - now
    hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
    minutes = remainder // 60
    reminder_str = next_reminder.astimezone(ZoneInfo("Etc/GMT-4")).strftime("%H:%M")
    update.message.reply_text(
        f"Я помню, что ближайшее напоминание будет в {reminder_str}, до него осталось {hours} часов и {minutes} минут."
    )
    print(f"Команда /test выполнена для chat_id {update.message.chat_id} в {datetime.now()} (UTC)")

# Команда /start
def start(update, context):
    chat_id = update.message.chat_id
    CHAT_IDS.add(chat_id)
    update.message.reply_text(
        "Спасибо, что подписался на напоминания о здоровье! 😊 "
        "Я буду напоминать тебе о таблетках в 6:00 и 20:00, а также о заботе о здоровье в 12:00. "
        "Чтобы остановить напоминания, используй /stop."
    )
    print(f"Пользователь с chat_id {chat_id} начал получать напоминания в {datetime.now()} (UTC)")

# Команда /stop
def stop(update, context):
    chat_id = update.message.chat_id
    if chat_id in CHAT_IDS:
        CHAT_IDS.remove(chat_id)
        update.message.reply_text("Напоминания остановлены. Чтобы возобновить, используй /start.")
        print(f"Пользователь с chat_id {chat_id} остановил напоминания в {datetime.now()} (UTC)")
    else:
        update.message.reply_text("Ты не подписан на напоминания. Используй /start, чтобы начать.")

# Получение chat_id
def get_chat_id(update, context):
    chat_id = update.message.chat_id
    update.message.reply_text(f"Ваш chat_id: {chat_id}")

# Обработчик кнопки
def button_callback(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "pill_taken":
        query.message.reply_text("Отлично! Ты выпил таблетки, молодец! 😊")
        if ADMIN_CHAT_ID:
            try:
                bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"Папа выпил таблетки, не забудь ему написать, спросить как дела! (chat_id: {query.message.chat_id})"
                )
                print(f"Уведомление админу отправлено в {datetime.now()} (UTC)")
            except Exception as e:
                print(f"Ошибка при отправке уведомления админу: {e}")

# Расписание (для +4 UTC: 6:00→2:00 UTC, 20:00→16:00 UTC, 12:00→8:00 UTC)
schedule.every().day.at("02:00").do(send_pill_reminder)  # 6:00 +4
schedule.every().day.at("16:00").do(send_pill_reminder)  # 20:00 +4
schedule.every().day.at("08:00").do(send_health_reminder)  # 12:00 +4

# Основная функция
def main():
    updater = Updater(TOKEN, use_context=True, request_kwargs={'connect_timeout': 10.0, 'read_timeout': 30.0})
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("get_chat_id", get_chat_id))
    dp.add_handler(CommandHandler("test", test))
    dp.add_handler(CallbackQueryHandler(button_callback))
    updater.start_polling()
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    main()