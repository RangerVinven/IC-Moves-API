from fastapi import APIRouter, Request, Response, status
from fastapi.responses import RedirectResponse

from utils.database_connector import cursor, db
from utils.authentication import get_session_token_from_request

router = APIRouter()

@router.get("/")
async def get_saved_properties(request: Request):
    session_token = get_session_token_from_request(request)

    if session_token == "":
        return RedirectResponse(url="/")

    cursor.execute("SELECT sp.property_id FROM SavedProperties sp JOIN Users u ON u.id = sp.user_id WHERE u.session_token=%s", (session_token,))
    return cursor.fetchall()

@router.get("/{property_id}")
async def save_properties(property_id: str, request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    # Redirects if the user isn't logged in
    if session_token == "":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    cursor.execute("SELECT id FROM Properties WHERE id=%s;", (property_id,))
    properties = cursor.fetchall()

    # Redirects if the property doesn't exist
    if len(properties) == 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    cursor.execute("SELECT id FROM Users WHERE session_token=%s", (session_token,))
    user_id = cursor.fetchone()["id"]

    cursor.execute("INSERT INTO SavedProperties (user_id, property_id) VALUES (%s, %s);", (user_id, property_id))
    db.commit()

    return RedirectResponse(url="/")

@router.delete("/{property_id}")
async def unsave_property(property_id: str, request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    # Redirects if the user isn't logged in
    if session_token == "":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    cursor.execute("DELETE FROM SavedProperties WHERE user_id=(SELECT id FROM Users WHERE session_token=%s) AND property_id=%s", (session_token, property_id))
    return
