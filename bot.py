# bot.py
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from rag_engine import query_rag

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я RAG-бот по вселенной Celestial Chronicles. Задайте вопрос."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    user_query = update.message.text
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )
    answer = query_rag(user_query)
    await update.message.reply_text(answer)


def main():
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30)   # таймаут подключения
        .read_timeout(30)      # таймаут чтения
        .write_timeout(30)     # таймаут записи
        .pool_timeout(30)      # таймаут пула соединений
        .build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    print("Бот запущен...")
    # bootstrap_retries=3 – три попытки при стартовом подключении, если сеть моргнула
    application.run_polling(
        allowed_updates=Update.ALL_TYPES, bootstrap_retries=3
    )

if __name__ == "__main__":
    main()
