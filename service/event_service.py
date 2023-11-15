import logging

from sqlalchemy.orm import Session
from sqlalchemy import select

from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from db.models import Event, User

logger = logging.getLogger(__name__)

class CustomCalendar(DetailedTelegramCalendar):
    size_year=4
    size_year_column=2

# TODO: async?
def save_event(user_id: int, date: str, event: str, session: Session):
    stmt = select(User).where(User.id == user_id)
    registered_user = session.scalar(stmt)
    
    if registered_user is None:
        # Handle the case where the user with the provided user_id doesn't exist
        logger.warn(f"User with id {user_id} not found.")
        return

    # Step 2: Create a new Event object
    new_event = Event(date=date, event=event)
    
    # Step 3: Associate the user with the event
    new_event.user = registered_user

    session.add(new_event)
    session.commit()

    return True