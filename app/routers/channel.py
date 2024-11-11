from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_channels():
    return {"message": "List of channels"}
