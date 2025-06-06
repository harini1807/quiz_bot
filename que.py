import os

TOKEN = os.getenv('BOT_TOKEN')
updater = Updater(TOKEN, use_context=True)

import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

from ques import QUESTIONS  # Import your questions dict

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# States for conversation
CHOOSE_TOPIC, ASK_QUESTION = range(2)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [[KeyboardButton(topic)] for topic in QUESTIONS.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    await update.message.reply_text(
        "Welcome to the Aptitude Quiz Bot!\nPlease choose a topic:",
        reply_markup=reply_markup)
    return CHOOSE_TOPIC


async def choose_topic(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> int:
    topic = update.message.text
    if topic not in QUESTIONS:
        await update.message.reply_text(
            "Invalid topic. Please choose from the list.")
        return CHOOSE_TOPIC

    # Store user's quiz data in context.user_data
    context.user_data['topic'] = topic
    context.user_data['question_index'] = 0
    context.user_data['score'] = 0

    return await ask_question(update, context)


async def ask_question(update: Update,
                       context: ContextTypes.DEFAULT_TYPE) -> int:
    topic = context.user_data['topic']
    index = context.user_data['question_index']

    if index >= len(QUESTIONS[topic]):
        score = context.user_data['score']
        await update.message.reply_text(
            f"Quiz finished! Your score: {score}/{len(QUESTIONS[topic])}")
        return ConversationHandler.END

    question = QUESTIONS[topic][index]
    keyboard = [[KeyboardButton(opt)] for opt in question['options']]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    await update.message.reply_text(f"{question['question']}",
                                    reply_markup=reply_markup)
    return ASK_QUESTION


async def handle_answer(update: Update,
                        context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'topic' not in context.user_data:
        await update.message.reply_text(
            "Please start a quiz first using /start")
        return ConversationHandler.END

    topic = context.user_data['topic']
    index = context.user_data['question_index']
    user_answer = update.message.text

    correct_index = QUESTIONS[topic][index]['answer']
    correct_answer_text = QUESTIONS[topic][index]['options'][correct_index]

    if user_answer == correct_answer_text:
        context.user_data['score'] += 1
        await update.message.reply_text("✅ Correct!")
    else:
        await update.message.reply_text(
            f"❌ Wrong! Correct answer: {correct_answer_text}")

    context.user_data['question_index'] += 1
    return await ask_question(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Quiz cancelled. See you next time!")
    return ConversationHandler.END


if __name__ == '__main__':
    from config import BOT_TOKEN  # Your bot token here

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSE_TOPIC:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_topic)],
            ASK_QUESTION:
            [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler('cancel', cancel)])

    app.add_handler(conv_handler)

    print("✅ Bot is running...")
    app.run_polling()
