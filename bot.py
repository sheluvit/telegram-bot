import random
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import os
TOKEN = os.environ.get("TOKEN")

DATA_FILE = "data.json"

calm_messages = [
    "Начни с 5 минут 📚",
    "Просто открой тетрадь",
    "Маленький шаг лучше, чем никакого",
    "Ты справишься 💪"
]

praise_messages = [
    "🔥 Молодец!",
    "👏 Отлично!",
    "💪 Так держать!",
    "🚀 Супер!"
]

keyboard = ReplyKeyboardMarkup(
    [
        ["🚀 Начать работу"],
        ["✅ Завершил"],
        ["📊 Статистика"]
    ],
    resize_keyboard=True
)

# загрузка данных
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# сохранение данных
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

user_stats = load_data()

# уровни
def get_level(count):
    if count <= 3:
        return "🌱 Новичок", 3
    elif count <= 8:
        return "🚀 Начал двигаться", 8
    elif count <= 15:
        return "💪 Продуктивный", 15
    elif count <= 25:
        return "🧠 Фокус-мастер", 25
    else:
        return "🔥 Машина", None

# старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)

    if user_id not in user_stats:
        user_stats[user_id] = {"done": 0}
        save_data(user_stats)

    await update.message.reply_text(
        "Привет 🙂 Я помогу тебе не прокрастинировать",
        reply_markup=keyboard
    )

# обработка кнопок
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    text = update.message.text

    if user_id not in user_stats:
        user_stats[user_id] = {"done": 0}

    # начать работу
    if text == "🚀 Начать работу":
        await update.message.reply_text(
            "Начни с 10–15 минут работы 💪"
        )

    # завершил задачу
    elif text == "✅ Завершил":
        user_stats[user_id]["done"] += 1
        count = user_stats[user_id]["done"]

        level, max_level = get_level(count)

        if max_level:
            remaining = max_level - count
            level_text = f"До следующего уровня осталось: {remaining}"
        else:
            level_text = "Ты достиг максимального уровня 🏆"

        save_data(user_stats)

        await update.message.reply_text(
            f"{random.choice(praise_messages)}\n\n"
            f"🏆 Уровень: {level}\n"
            f"📊 Всего выполнено: {count}\n"
            f"{level_text}"
        )

    # статистика
    elif text == "📊 Статистика":
        count = user_stats[user_id]["done"]

        await update.message.reply_text(
            f"📊 Ты выполнил {count} задач"
        )

# запуск бота
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling(drop_pending_updates=True)