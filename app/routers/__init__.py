from fastapi import APIRouter
from .chat import router as chat_router
from .user import router as user_router
from .channel import router as channel_router

# Объедините все маршруты
router = APIRouter()
router.include_router(chat_router, prefix="/chat", tags=["chat"])
router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(channel_router, prefix="/channel", tags=["channel"])
