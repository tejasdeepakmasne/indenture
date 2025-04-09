from pydantic import BaseModel
from enum import Enum

class TaskType(Enum):
    REST = "rest"
    SHELL = "shell"

class Task(BaseModel):
    Name: str
    Type: TaskType
    