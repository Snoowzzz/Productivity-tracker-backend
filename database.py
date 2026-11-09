
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

Base = declarative_base()

SQLALCHEMY_DATABASE_URL = "sqlite:///./productivity.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind = engine,autoflush = False)

def get_db():
    db = SessionLocal()
    try:
        #perform our database operations here
        yield db
    finally:
        db.close()
    