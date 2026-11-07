from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    title: str
    description :str

dct = {}

@app.get("/")
def home():
    return "Hello how are you!!"


@app.get("/tasks")
def tasks():
    return dct.items()


@app.get("/tasks/{task_id}")
def id(task_id : int):
    for i,v in dct.items():
        if i == task_id:
            return dct[task_id]
        
        
@app.post("/tasks")
def create():
    new_id = max(p["id"] for p in task) + 1 if task else 1
    task = {
        "id":1,
        "title":"LearnFastApi",
        "description": "Your boy is struggling"
        }
    
@app.put("/tasks/{task_id}")
def update(task_id: int):
    for i in dct.keys():
          