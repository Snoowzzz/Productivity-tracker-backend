# ## practising the previous files here
# ## database.py
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker,declarative_base

# Base = declarative_base()

# SQLURL = "sqlite:///./prod.db"
# engine = create_engine(
#     SQLURL,
#     connect_args={"check_same_thread" :False}
#     )

# SessionLocal = sessionmaker(bind=engine,autoflush=False)

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
        
        
# ## models
# from sqlalchemy import String, Integer, Column
# from database import Base

# class Task(Base):
#     __tablename__ = "tasks"
#     id = Column(Integer, primary_key= True, index= True)
#     title = Column(String,nullable= False)
#     description = Column(String,nullable= True)
    
from fastapi import Depends,FastAPI
from sqlalchemy.orm import Session
from models import Task
from schemas import TaskResponse,TaskCreate
from database import Base,engine,get_db
app = FastAPI()

Base.metadata.create_all(bind= engine)

@app.get("/")
def home():
    return "Hey Handsome how are you"

@app.post("/tasks",response_model=TaskResponse,status_code=201)
def create_task(
    task:Task,
    db: Session = Depends(get_db), ):
    new_task = Task(
        title = task.title,
        description = task.description,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task