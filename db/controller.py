import logging
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import select
from telegram import User as TelegramUser

from db.models import Event, User

logger = logging.getLogger(__name__)

# TODO: async?
def save_event(user_id: int, date: date, event: str, session: Session):
    stmt = select(User).where(User.id == user_id)
    registered_user = session.scalar(stmt)
    
    if registered_user is None:
        logger.warn(f"User with id {user_id} not found.")
        return False

    new_event = Event(date=date, event=event)
    new_event.user = registered_user

    session.add(new_event)
    session.commit()

    return True

def list_events(user_id: int, session: Session):
    stmt = select(Event).where(user_id==user_id)
    events = session.scalars(stmt)
    return events.all()


# TODO: create a separate class
# TODO: async?
def register_user(user: TelegramUser, session: Session):
    stmt = select(User).where(User.id == user.id)
    registered_user = session.scalar(stmt)
    if registered_user:
        return False
    else:
        new_user = User(
        id=user.id,
        username=user.username,
        )
        session.add(new_user)
        session.commit()
        return True