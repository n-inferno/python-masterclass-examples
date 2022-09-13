# Пример взят отсюда:
# https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot.py
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters

DURATION, MEMBERS = 1, 2
user = {}


async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот для создания встреч!", )


async def new_meeting_handler(update, context):
    user.clear()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите длительность встречи (число от 5 до 540)",
    )
    return DURATION


async def duration_handler(update, context):
    duration = update.message.text

    if not duration.isdigit():
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите, пожалуйста, число.",
        )
        return DURATION

    duration = int(duration)
    if not 5 <= duration <= 540:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Число должно быть больше 5 и меньше 540.",
        )
        return DURATION

    user["duration"] = duration
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Отлично!")
    return MEMBERS


if __name__ == '__main__':
    application = ApplicationBuilder().token("TOKEN").build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("meeting", new_meeting_handler)],
        states={
            DURATION: [MessageHandler(filters.TEXT, duration_handler)],
            MEMBERS: [],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.run_polling()
