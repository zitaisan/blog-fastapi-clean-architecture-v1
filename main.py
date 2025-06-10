from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI()

# =============================
# Модели данных
# =============================

class Task:
    def __init__(self, id: int, title: str, description: str, completed: bool = False,
                 project_id: Optional[int] = None, user_id: Optional[int] = None):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed
        self.project_id = project_id
        self.user_id = user_id
        self.created_at = datetime.now()

class Project:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

class User:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email


# =============================
# Схемы для валидации
# =============================

class TaskCreateSchema(BaseModel):
    title: str
    description: str
    completed: bool = False
    project_id: Optional[int] = None
    user_id: Optional[int] = None

class TaskUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    project_id: Optional[int] = None
    user_id: Optional[int] = None

class TaskResponseSchema(TaskCreateSchema):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectCreateSchema(BaseModel):
    name: str

class ProjectResponseSchema(ProjectCreateSchema):
    id: int

    class Config:
        from_attributes = True

class UserCreateSchema(BaseModel):
    name: str
    email: str

class UserResponseSchema(UserCreateSchema):
    id: int

    class Config:
        from_attributes = True


# =============================
# In-memory репозитории (паттерн Repository)
# =============================

class BaseRepository:
    def __init__(self):
        self._storage = {}
        self._counter = 1

    def add(self, item):
        item.id = self._counter
        self._storage[self._counter] = item
        self._counter += 1
        return item

    def get(self, item_id):
        return self._storage.get(item_id)

    def list(self):
        return list(self._storage.values())

    def delete(self, item_id):
        if item_id in self._storage:
            del self._storage[item_id]
            return True
        return False

    def update(self, item_id, data):
        item = self._storage.get(item_id)
        if not item:
            return None
        for key, value in data.items():
            setattr(item, key, value)
        return item


task_repository = BaseRepository()
project_repository = BaseRepository()
user_repository = BaseRepository()


# =============================
# API Endpoints
# =============================

# --- Tasks ---

@app.post("/tasks/", response_model=TaskResponseSchema)
def create_task(task_data: TaskCreateSchema):
    task = Task(**task_data.dict())
    return task_repository.add(task)

@app.get("/tasks/{task_id}", response_model=TaskResponseSchema)
def read_task(task_id: int):
    task = task_repository.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.get("/tasks/", response_model=List[TaskResponseSchema])
def read_tasks():
    return task_repository.list()

@app.put("/tasks/{task_id}", response_model=TaskResponseSchema)
def update_task(task_id: int, task_data: TaskUpdateSchema):
    updated = task_repository.update(task_id, task_data.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    success = task_repository.delete(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success", "message": "Task deleted"}

# --- Projects ---

@app.post("/projects/", response_model=ProjectResponseSchema)
def create_project(project_data: ProjectCreateSchema):
    project = Project(**project_data.dict())
    return project_repository.add(project)

@app.get("/projects/", response_model=List[ProjectResponseSchema])
def read_projects():
    return project_repository.list()

# --- Users ---

@app.post("/users/", response_model=UserResponseSchema)
def create_user(user_data: UserCreateSchema):
    user = User(**user_data.dict())
    return user_repository.add(user)

@app.get("/users/", response_model=List[UserResponseSchema])
def read_users():
    return user_repository.list()