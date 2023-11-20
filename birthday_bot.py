import logging
import os
import datetime

from telegram import (
    Update,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    filters,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
)

from telegram_bot_calendar import LSTEP

from db import Session
from service.user_service import register_user
from service.event_service import CustomCalendar, save_event

DATE, EVENT = range(2)

# TODO: use proper logging (check telegram package docs)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# TODO: brush up on the concurrency in telegram package (telegram package docs)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    with Session.begin() as session:
        result = register_user(user=user, session=session)
        if result:
            response_text = f"We are now ready to remember birthday dates for you, {user.username}!"
        else:
            response_text = f"Yes, we remember you, {user.username}!"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=response_text,
        )


async def remember_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Please enter a date for the memorable event"
    )
    
    calendar, step = CustomCalendar().build()
    await update.message.reply_text(
        f"Select {LSTEP[step]}",
        reply_markup=calendar
    )
    
    return DATE

async def enter_event(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    event = update.message.text
    # datetime.date is saved here
    event_date = context.user_data["date"]
    with Session.begin() as session:
        save_event(user_id=update.effective_user.id, date=event_date, event=event, session=session)
    # TODO: rework the reply
    # mention how many days left before the event
    delta1 = datetime.date(datetime.date.today().year, event_date.month, event_date.day)
    delta2 = datetime.date(datetime.date.today().year + 1, event_date.month, event_date.day)
    days_before_event = ((delta1 if delta1 > datetime.date.today() else delta2) - datetime.date.today()).days
    text = (
        f"{days_before_event} days before the event.\n"
        "You will be reminded of this event a week before selected date "
        "and then a day before selected date"
    )
    await update.message.reply_text(text)
    return ConversationHandler.END


async def calendar_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    result, key, step = CustomCalendar().process(query.data)

    if not result and key:
        await query.edit_message_text(text=f"Select {LSTEP[step]}", reply_markup=key)
    elif result:
        text = (f"{result}\nGreat! And what do you want to be reminded of for this date?\n")
        context.user_data["date"] = result
        
        await query.edit_message_text(text)
        return EVENT



async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info(f"User {user} canceled the conversation.")
    await update.message.reply_text(
        "Bye! I hope we can talk again later.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# TODO: check the proper architecture (telegram package docs)
if __name__ == "__main__":

    bot_token = os.environ.get("TOKEN")
    application = ApplicationBuilder().token(bot_token).build()

    # Add conversation handler with the states NAME, DATE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("event", remember_event)],
        states={
            DATE: [CallbackQueryHandler(calendar_button)],
            EVENT: [MessageHandler(filters.TEXT, enter_event)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    start_handler = CommandHandler(command='start', callback=start)
    application.add_handler(start_handler)
    application.add_handler(conv_handler)

    application.run_polling()
