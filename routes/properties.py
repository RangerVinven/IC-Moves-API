from fastapi import APIRouter, Request, Response, status

from utils.database_connector import cursor, db
from utils.authentication import get_session_token_from_request

router = APIRouter()

@router.get("/")
async def get_properties():
    cursor.execute("SELECT id, name, bedrooms, showers, noise_level, rent, folder FROM Properties ORDER BY id asc;")
    properties = cursor.fetchall()

    cursor.execute("SELECT property_id, alt_description FROM Images WHERE image_number=1 ORDER BY property_id asc;")
    images = cursor.fetchall()

    for i in range(len(properties)):
        properties[i]["alt_description"] = images[i]["alt_description"]

    return properties

@router.get("/{property_id}/is_saved")
async def is_property_saved(property_id: str, request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    if session_token == "":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    # Gets a list of properties with the property_id and session_token
    cursor.execute("SELECT property_id FROM SavedProperties sp JOIN Users u ON sp.user_id = u.id WHERE sp.property_id=%s AND u.session_token=%s", (property_id, session_token))
    properties = cursor.fetchall()

    # Length = 0 if the property isn't saved
    if len(properties) == 0:
        return False

    else:
        return True

@router.get("/{property_id}")
async def get_property(property_id: str):
    # Gets all the information about a property
    cursor.execute("SELECT * FROM Properties WHERE id=%s;", (property_id,))
    return cursor.fetchone()
