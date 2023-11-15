import logging
import os
from telegram import User as TelegramUser

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import User

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
