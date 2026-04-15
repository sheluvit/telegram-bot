import random
import json
import os

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("TOKEN")

DATA_FILE = "data.json"

# загрузка данных
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

user_stats = load_data()
active_users = set()

# клавиатура
keyboard = ReplyKeyboardMarkup(
    [
        ["🚀 Начать работу"],
        ["✅ Завершил"],
        ["📊 Статистика"]
    ],
    resize_keyboard=True
)

# ====== ФРАЗЫ ======

reminder_messages = [
    "📵 Хватит скроллить — начни делать домашку",
    "⏳ 10 минут работы сейчас лучше, чем 2 часа прокрастинации",
    "📚 Открой тетрадь и сделай хотя бы 1 шаг",
    "🚀 Если уже сделал — нажми «✅ Завершил»",
    "💪 Ты либо отдыхаешь, либо двигаешься вперёд",
    "🔥 Просто начни. Без настроения."
]

praise_messages = [
    "🔥 Отлично! Ты реально сделал это",
    "💪 Вот это дисциплина",
    "🚀 Красавчик, продолжай в том же духе",
    "👏 Ты не откладываешь — ты делаешь",
    "🏆 Ещё один шаг вперёд"
]

motivation_messages = [
    "Начни сейчас — и через 20 минут ты уже в процессе 💪",
    "Ты уже ближе к цели, чем думаешь",
    "Маленькие действия дают большие результаты",
    "Сделай сейчас — и потом будешь свободен",
    "Ты можешь больше, чем тебе кажется"
]

study_messages = [
    "10 минут концентрации = меньше стресса вечером",
    "Сначала дело — потом отдых",
    "Закрой один маленький пункт из списка задач",
    "Учёба не станет легче, если её откладывать",
    "Сделай задачу сейчас и выдохни спокойно"
]

# ====== УРОВНИ ======

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

# ====== СТАРТ ======

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)

    active_users.add(user_id)

    if user_id not in user_stats:
        user_stats[user_id] = {"done": 0}
        save_data(user_stats)

    await update.message.reply_text(
        "Привет 🙂 Я помогу тебе не прокрастинировать",
        reply_markup=keyboard
    )

# ====== НАПОМИНАНИЯ ======

async def send_reminders(context: ContextTypes.DEFAULT_TYPE):
    for user_id in list(active_users):
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=random.choice(reminder_messages)
            )
        except:
            pass

# ====== ОБРАБОТКА КНОПОК ======

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.chat_id)
    text = update.message.text

    if user_id not in user_stats:
        user_stats[user_id] = {"done": 0}

    # начать работу
    if text == "🚀 Начать работу":
        await update.message.reply_text(
            random.choice(motivation_messages)
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

# ====== ЗАПУСК ======

app = ApplicationBuilder().token(TOKEN).build()


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# job queue (напоминания)
job_queue = app.job_queue
job_queue.run_repeating(
    send_reminders,
    interval=60 * 60,  # 1 час (можешь поменять на 2 часа = 7200)
    first=10
)

app.run_polling(drop_pending_updates=True)
