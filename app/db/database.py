from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from app.config import settings

# URL-encode the password to handle special characters like @
encoded_password = quote_plus(settings.database_password)

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.database_username}:{encoded_password}"
    f"@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
