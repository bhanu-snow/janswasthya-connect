import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base


DB_USER = os.getenv("DB_USER", "janswasthya_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "janswasthya_password")
DB_HOST = os.getenv("DB_HOST", "mariadb")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "janswasthya")


DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


Base = declarative_base()
