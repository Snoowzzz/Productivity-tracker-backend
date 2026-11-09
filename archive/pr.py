## practising the previous files here
## database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

Base = declarative_base()

SQLURL = "sqlite:///./prod.db"
engine = create_engine(
    SQLURL,
    connect_args={"check_same_thread" :False}
    )

SessionLocal = sessionmaker(bind=engine,autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()