from datetime import date

from sqlalchemy import (
    String,
    ForeignKey,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)

class Base(DeclarativeBase):
    pass


# Will make it personal for now
class Chat(Base):
    __tablename__ = "chats"

    # telegram chat_id 
    id: Mapped[int] = mapped_column(primary_key=True)
    events: Mapped[list["Event"]] = relationship(
        back_populates="chat", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return self.id


class Event(Base):
    __tablename__  = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event: Mapped[str] = mapped_column(String(30))
    date: Mapped[date]
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    chat: Mapped["Chat"] = relationship(back_populates="events")

    def __repr__(self) -> str:
        return super().__repr__()