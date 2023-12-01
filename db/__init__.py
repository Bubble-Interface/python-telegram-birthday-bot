import os
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import (
    sessionmaker,
)
    
from db.models import (
    Base,
)

db_user = os.environ.get("POSTGRES_USER", 'user')
db_pass = os.environ.get("POSTGRES_PASSWORD", 'password')
db_host = os.environ.get("DB_HOST", 'birthday_bot_postgres')
db_port = os.environ.get("DB_PORT", '5432')
db_name = os.environ.get("POSTGRES_DB", 'birthday')

db_string = f'postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

if not database_exists(db_string):
    create_database(db_string)
engine = create_engine(db_string)

Session = sessionmaker(engine)
Base.metadata.create_all(engine)
