from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm your quiz bot. Use /quiz to start!")

app = ApplicationBuilder().token("8001147018:AAHKNXD8_znh05J7YS0v0saxMqtHqOMrKv0").build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
