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
        
        
## models
from sqlalchemy import String, Integer, Column
from database import Base

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key= True, index= True)
    title = Column(String,nullable= False)
    description = Column(String,nullable= True)
    