# Пример взят из официальной документации:
# https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions-%E2%80%93-Your-first-Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters


async def start(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Я бот для создания встреч!",
    )


async def handler(update, context):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=update.message.text,
    )


if __name__ == "__main__":
    application = ApplicationBuilder().token("TOKEN").build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    handler = MessageHandler(filters.TEXT, handler)
    application.add_handler(handler)

    application.run_polling()


