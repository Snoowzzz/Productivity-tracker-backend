from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description : str
    
# # Outgoing task data
class TaskResponse(TaskCreate):
    id : int