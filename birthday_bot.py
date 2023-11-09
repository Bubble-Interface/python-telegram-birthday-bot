import logging
import os

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
from service.birthday_service import CustomCalendar

NAME, DATE = range(2)

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


async def remember_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Please enter a name of the person"
    )
    
    return NAME

async def enter_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    name = update.message.text
    logger.info(f"New Birthday record for: {name}")
    context.user_data["name"] = name
    calendar, step = CustomCalendar().build()
    await update.message.reply_text(
        "Great!\n"
        f"And when was {name} born?\n"
    )
    await update.message.reply_text(
        f"Select {LSTEP[step]}",
        reply_markup=calendar
    )
    return DATE

async def select_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    result, key, step = CustomCalendar().process(query.data)

    if not result and key:
        await query.edit_message_text(text=f"Select {LSTEP[step]}", reply_markup=key)
    elif result:
        text = f"I remembered {context.user_data['name']} birthday: {result}"
        logger.info(f"New Birthday record for: {context.user_data['name']}, {result}")
        await query.edit_message_text(text)
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again later.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

# TODO: check the proper architecture (telegram package docs)
# TODO: figure out a way to work in private chats and groups
if __name__ == "__main__":

    bot_token = os.environ.get("TOKEN")
    application = ApplicationBuilder().token(bot_token).build()

    # Add conversation handler with the states NAME, DATE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("birthday", remember_birthday)],
        states={
            NAME: [MessageHandler(filters.TEXT, enter_name)],
            DATE: [CallbackQueryHandler(select_date)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    start_handler = CommandHandler(command='start', callback=start)
    application.add_handler(start_handler)
    application.add_handler(conv_handler)

    application.run_polling()
