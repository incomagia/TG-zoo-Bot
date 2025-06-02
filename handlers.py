# Здесь будут обработчики для Telegram-бота

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from quiz_data import quiz_questions, animal_ids, animal_profiles

# Временное хранилище для состояния пользователя
user_data = {}

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^[0-2]$"))
    app.add_handler(CallbackQueryHandler(restart_quiz, pattern="^restart$"))
    app.add_handler(CallbackQueryHandler(feedback_prompt, pattern="^feedback$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_feedback))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {
        "score": {key: 0 for key in animal_ids},
        "current_q": 0,
        "expecting_feedback": False
    }
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет, {0}! Добро пожаловать в викторину Московского зоопарка! 🦁\n\nОтветь на несколько вопросов, и мы определим твоё тотемное животное.".format(update.effective_user.first_name)
    )
    await send_question(update, context)

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    state = user_data[user_id]
    q_index = state["current_q"]

    if q_index >= len(quiz_questions):
        await show_result(update, context)
        return

    question = quiz_questions[q_index]
    buttons = [
        [InlineKeyboardButton(opt, callback_data=str(i))] 
        for i, opt in enumerate(question["options"])
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=question["text"],
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    answer_index = int(query.data)

    state = user_data[user_id]
    current_question = state["current_q"]

    # Увеличить счёт выбранному животному
    chosen_animal = animal_ids[answer_index]
    state["score"][chosen_animal] += 1

    # Переходим к следующему вопросу
    state["current_q"] += 1
    await send_question(update, context)

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    score = user_data[user_id]["score"]

    # Найти животное с максимальным числом очков
    best_animal_id = max(score, key=score.get)
    profile = animal_profiles[best_animal_id]

    with open(profile["image_path"], "rb") as img:
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=img,
            caption=f"{profile['description']}\n\nСпасибо за прохождение!"
        )

    # Кнопки после результата
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Пройти ещё раз", callback_data="restart")
        ],
        [
            InlineKeyboardButton("Оставить отзыв", callback_data="feedback")
        ]
    ])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Хочешь попробовать ещё раз или оставить отзыв?",
        reply_markup=buttons
    )

async def restart_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_data[user_id] = {
        "score": {key: 0 for key in animal_ids},
        "current_q": 0,
        "expecting_feedback": False
    }
    await send_question(update, context)

async def feedback_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_data[user_id]["expecting_feedback"] = True

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Пожалуйста, напиши свой отзыв в одном сообщении:"
    )

# Отзыв
async def receive_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data and user_data[user_id].get("expecting_feedback"):
        user_data[user_id]["expecting_feedback"] = False
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Спасибо за отзыв! Он отправлен нашей команде 📨"
        )

        # Повторное предложение начать заново
        button = InlineKeyboardMarkup([[InlineKeyboardButton("Пройти ещё раз", callback_data="restart")]])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Хочешь пройти викторину снова?",
            reply_markup=button
        )
