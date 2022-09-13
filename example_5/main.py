from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters, \
    CallbackQueryHandler

from example_5 import staff, config
from example_5.helpers import get_meetings_options
from example_5.staff import get_employees_calendars, create_calendar_event

DURATION, MEMBERS, SUBMIT = 1, 2, 3
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
    user["emails"] = [config.USER_EMAIL]
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Отлично! Введите имя первого участника")
    return MEMBERS


async def name_handler(update, context):
    response = update.message.text

    if response.lower() == "далее":
        # округляем до целого часа
        t = datetime.now(tz=ZoneInfo(config.USER_TIME_ZONE))
        if t.minute >= 30:
            t = t.replace(second=0, microsecond=0, minute=0, hour=t.hour + 1)
        else:
            t = t.replace(second=0, microsecond=0, minute=0)

        dt_from = t
        dt_to = t + timedelta(days=config.MEETING_PERIOD)

        # получаем данные календаря
        calendars = await get_employees_calendars(user["emails"], dt_from, dt_to)

        # ищем свободное время в ближайшие N дней
        options = await get_meetings_options(calendars, user["duration"], dt_from, dt_to)

        if not options:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="К сожалению, у участников нет свободных слотов в указанный период. "
                     "Возможно стоит увеличить количество дней поиска в настройках.",
            )
            return ConversationHandler.END

        option = options[0]
        user["suggestion"] = option
        emails = '\n'.join(user["emails"])

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Предлагаю встречу {option[0].strftime('%d.%m')} c {option[0].strftime('%H:%M')} до {option[1].strftime('%H:%M')}.\n"
                 f"Нажмите \"Подтвердить\" чтобы отправить приглашение участникам:\n{emails}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Подтвердить", callback_data="submit")],
                [InlineKeyboardButton("Отмена", callback_data="cancel")],
            ])
        )
        return SUBMIT

    results = await staff.search_person_email(response)

    if not results:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="По данному запросу совпадений не найдено.",
        )
        return MEMBERS

    keyboard = [[InlineKeyboardButton(person["name"], callback_data=person["email"])] for person in results[:4]]
    keyboard.append([InlineKeyboardButton("Ввести другое имя", callback_data="other")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вот что удалось найти в Стаффе. Выберите из предложенных вариантов или попробуйте другой запрос.",
        reply_markup=reply_markup,
    )
    return MEMBERS


async def name_callback_handler(update, context):
    await update.callback_query.answer()

    response = update.callback_query.data

    if response == "other":
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите запрос.",
        )
        return MEMBERS

    user["emails"].append(response)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите имя следующего участника. Чтобы перейти к выбору встречи, введите 'далее'"
    )
    return MEMBERS


async def submit(update, context):
    await update.callback_query.answer()

    response = update.callback_query.data

    if response == "submit":
        await create_calendar_event(user["emails"], user["suggestion"][0], user["suggestion"][1])
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Приглашение отправлено участникам.",
        )
    if response == "cancel":
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Выбор отменен.")

    return ConversationHandler.END


if __name__ == '__main__':
    application = ApplicationBuilder().token(config.TOKEN).build()

    start_handler = CommandHandler("start", start)
    application.add_handler(start_handler)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("meeting", new_meeting_handler)],
        states={
            DURATION: [MessageHandler(filters.TEXT, duration_handler)],
            MEMBERS: [MessageHandler(filters.TEXT, name_handler), CallbackQueryHandler(name_callback_handler)],
            SUBMIT: [CallbackQueryHandler(submit)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.run_polling()
