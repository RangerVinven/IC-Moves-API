from fastapi import APIRouter, Request, Response, status

from utils.database_connector import cursor, db
from utils.authentication import get_session_token_from_request

router = APIRouter()

@router.get("/")
async def get_saved_properties(request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    if session_token == "":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    cursor.execute("SELECT sp.property_id FROM SavedProperties sp JOIN Users u ON u.id = sp.user_id WHERE u.session_token=%s", (session_token,))
    return cursor.fetchall()

@router.get("/{property_id}")
async def save_property(property_id: str, request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    # Redirects if the user isn't logged in
    if session_token == "":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    # Ensures the property exists
    cursor.execute("SELECT id FROM Properties WHERE id=%s;", (property_id,))
    properties = cursor.fetchall()

    if len(properties) == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    # Gets the user's id
    cursor.execute("SELECT id FROM Users WHERE session_token=%s;", (session_token,))
    user_id = cursor.fetchone()["id"]

    # Doesn't add to the database if it's already saved
    cursor.execute("SELECT property_id FROM SavedProperties WHERE user_id=%s AND property_id=%s;", (user_id, property_id))
    if len(cursor.fetchall()) != 0:
        return

    cursor.execute("INSERT INTO SavedProperties (user_id, property_id) VALUES (%s, %s);", (user_id, property_id))
    db.commit()

    return

@router.delete("/{property_id}")
async def unsave_property(property_id: str, request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    # Redirects if the user isn't logged in
    if session_token == "":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    cursor.execute("DELETE FROM SavedProperties WHERE user_id=(SELECT id FROM Users WHERE session_token=%s) AND property_id=%s", (session_token, property_id))
    return
