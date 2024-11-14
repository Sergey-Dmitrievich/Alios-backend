from fastapi import FastAPI
from .database import engine, Base
from .routers import router
from .routers import router
from fastapi.middleware.cors import CORSMiddleware






# Создание экземпляра FastAPI
app = FastAPI()
app.include_router(router, prefix="/api")

# Создание всех таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Подключение маршрутизаторов


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Укажите ваши источники, если нужно
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
