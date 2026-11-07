from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# Incoming task data
class Task(BaseModel):
    title: str
    description: str


# Outgoing task data
class TaskResponse(Task):
    id: int


# Temporary database
tasks_db = {}


@app.get("/")
def home():
    return "Hello how are you!!"


# GET all tasks
@app.get("/tasks", response_model=list[TaskResponse])
def get_tasks():
    return list(tasks_db.values())


# GET a particular task
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):

    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    return tasks_db[task_id]


# CREATE a task
@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: Task):

    new_id = max(tasks_db.keys(), default=0) + 1

    new_task = {
        "id": new_id,
        **task.model_dump()
    }

    tasks_db[new_id] = new_task

    return new_task


# UPDATE a task
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, updated_task: Task):

    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    tasks_db[task_id] = {
        "id": task_id,
        **updated_task.model_dump()
    }

    return tasks_db[task_id]


# DELETE a task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):

    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    del tasks_db[task_id]

    return {"message": "Task deleted successfully"}