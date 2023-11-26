import logging
from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy import select
from telegram import User as TelegramUser

from db.models import Event, Chat

logger = logging.getLogger(__name__)

# TODO: async?
def save_event(chat_id: int, date: date, event: str, session: Session):
    stmt = select(Chat).where(Chat.id == chat_id)
    registered_chat = session.scalar(stmt)
    
    if registered_chat is None:
        logger.warn(f"Chat with id {chat_id} not found.")
        return False

    new_event = Event(date=date, event=event)
    new_event.chat = registered_chat

    session.add(new_event)
    session.commit()

    return True

def list_events_for_chat(chat_id: int, session: Session):
    stmt = select(Event).where(chat_id==chat_id)
    events = session.scalars(stmt)
    return events.all()

def get_chat(session: Session):
    stmt = select(Chat)
    chat = session.scalar(stmt)
    return chat

# TODO: create a separate class
# TODO: async?
def register_chat(chat_id: int, session: Session):
    stmt = select(Chat).where(Chat.id == chat_id)
    registered_user = session.scalar(stmt)
    if registered_user:
        return False
    else:
        new_user = Chat(
            id=chat_id,
        )
        session.add(new_user)
        session.commit()
        return True
