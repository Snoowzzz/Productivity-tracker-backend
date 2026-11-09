
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "sqlite:///./productivity.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
