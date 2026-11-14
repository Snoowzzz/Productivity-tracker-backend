
from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import Task
from schemas import TaskCreate, TaskResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return "Hello how are you!!"


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):

    new_task = Task(
        title=task.title,
        description=task.description
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

@app.get("/tasks",response_model=list[TaskResponse],status_code=200)
def get_tasks(db: Session = Depends(get_db)):
    task = db.query(Task).all()
    return task

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):

    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task