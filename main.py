from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    title: str
    description :str

dct = {
    
}

@app.get("/")
def home():
    return "Hello how are you!!"

# @app.get("/")