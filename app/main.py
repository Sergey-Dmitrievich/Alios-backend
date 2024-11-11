from fastapi import FastAPI
from .database import engine, Base
from .routers import router

# Создание экземпляра FastAPI
app = FastAPI()

# Создание всех таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Подключение маршрутизаторов
app.include_router(router)
