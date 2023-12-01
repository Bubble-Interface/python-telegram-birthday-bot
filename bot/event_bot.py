import logging
import datetime
from pytz import timezone 

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
from db.controller import (
    register_chat,
    save_event,
    list_events_for_chat,
    get_events_reminder_events
)
from bot import CustomCalendar

DATE, EVENT = range(2)

logger = logging.getLogger(__name__)

class EventBot():
    def __init__(self, token) -> None:
        self.application = ApplicationBuilder().token(token).build()
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("event", self.remember_event)],
            states={
                DATE: [CallbackQueryHandler(self.calendar_button)],
                EVENT: [MessageHandler(filters.TEXT, self.enter_event)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        start_handler = CommandHandler(command='start', callback=self.start)
        all_events_handler = CommandHandler(command='events', callback=self.all_events)
    
        self.application.add_handler(start_handler)
        self.application.add_handler(conv_handler)
        self.application.add_handler(all_events_handler)

        job_queue = self.application.job_queue

        reminder_job = job_queue.run_daily(
            callback=self.reminder, 
            # TODO: use config file for these values
            time=datetime.time(hour = 10, minute = 00, tzinfo=timezone('Europe/Moscow')),
            days=(0, 1, 2, 3, 4, 5, 6),
        )
    
    def run(self):
        self.application.run_polling()


    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        with Session.begin() as session:
            result = register_chat(chat_id=chat_id, session=session)
            if result:
                response_text = f"We are now ready to remember birthday dates for you!"
            else:
                response_text = f"Thank you for using this bot!.\nPlease use the commands listed in the menu."
            await context.bot.send_message(
                chat_id=chat_id,
                text=response_text,
            )


    async def remember_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text(
            "Please enter a date for the memorable event"
        )

        calendar, step = CustomCalendar().build()
        await update.message.reply_text(
            f"Select {LSTEP[step]}",
            reply_markup=calendar
        )

        return DATE

    async def enter_event(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        event = update.message.text
        # datetime.date is saved here
        event_date = context.user_data["date"]
        chat_id = update.effective_chat.id
        with Session.begin() as session:
            save_event(chat_id=chat_id, date=event_date, event=event, session=session)

        this_year = datetime.date(datetime.date.today().year, event_date.month, event_date.day)
        next_year = this_year.replace(year=this_year.year + 1)
        days_before_event = ((this_year if this_year > datetime.date.today() else next_year) - datetime.date.today()).days
        text = (
            f"{days_before_event} days before the event.\n"
            "You will be reminded of this event a week before selected date "
            "and then a day before selected date"
        )
        await update.message.reply_text(text)
        return ConversationHandler.END


    async def calendar_button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        result, key, step = CustomCalendar().process(query.data)

        if not result and key:
            await query.edit_message_text(text=f"Select {LSTEP[step]}", reply_markup=key)
        elif result:
            text = (f"{result}\nGreat! And what do you want to be reminded of for this date?\n")
            context.user_data["date"] = result

            await query.edit_message_text(text)
            return EVENT


    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        logger.info(f"User {user} canceled the conversation.")
        await update.message.reply_text(
            "Bye! I hope we can talk again later.", reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

    async def all_events(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        chat_id = update.effective_chat.id
        with Session.begin() as session:
            events = list_events_for_chat(chat_id=chat_id, session=session)
            # TODO: custom reply for no events
            events_text = "\n\n".join([f"Event date: {event.date}.\nEvent description: {event.event}" for event in events])
            reply_text = (
                f"Here's you're list of events:\n\n"
                f"{events_text}"
            )
            await update.message.reply_text(reply_text)

    
    async def reminder(self, context: ContextTypes.DEFAULT_TYPE):
        todays_date = datetime.date.today()
        tomorrows_date = todays_date + datetime.timedelta(days=1)
        in_a_week_date = todays_date + datetime.timedelta(days=7)
        with Session.begin() as session:
            events = get_events_reminder_events(session=session)
            for event in events:
                event_date_this_year = event.date.replace(year=todays_date.year)
                if event_date_this_year == tomorrows_date:
                    text = f"Tomorrow ({event.date}) this event will take place:\n{event.event}"
                elif event_date_this_year == in_a_week_date:
                    text = f"In a week ({event.date}) this event will take place:\n{event.event}"
                await context.bot.send_message(chat_id=event.chat_id, text=text)

    
    