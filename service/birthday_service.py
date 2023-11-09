from sqlalchemy.orm import Session
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


class CustomCalendar(DetailedTelegramCalendar):
    size_year=4
    size_year_column=2


async def remember_birthday(session: Session):
    pass