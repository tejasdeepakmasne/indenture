from pydantic import BaseModel
from enum import Enum

class TaskType(Enum):
    REST = "rest"
    SHELL = "shell"
    

    
class REST_config(BaseModel):
    Method: 

class Task(BaseModel):
    Name: str
    Type: TaskType
    Dependens_on: list
    Conditions:list
    