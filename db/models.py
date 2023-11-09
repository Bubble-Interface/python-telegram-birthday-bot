

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
class User(Base):
    __tablename__ = "users"

    # telegram user_id 
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30))
    birthdays: Mapped[list["Birthday"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return self.username


# TODO: add the ability to mention a telegram user
class Birthday(Base):
    __tablename__  = "birthdays"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_name: Mapped[str] = mapped_column(String(30))
    # TODO: replace with the date type
    date: Mapped[str] = mapped_column(String(30))
    originator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="birthdays")

    def __repr__(self) -> str:
        return super().__repr__()