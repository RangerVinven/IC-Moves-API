from fastapi import APIRouter
from utils.database_connector import cursor

router = APIRouter()

# Gets the images for a property
@router.get("/{property_id}")
async def get_images(property_id: str):
    cursor.execute("SELECT * FROM Images WHERE property_id=%s;", (property_id,))
    return cursor.fetchall()