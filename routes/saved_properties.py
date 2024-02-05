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

    # Gets the property information of the saved images
    cursor.execute("SELECT p.id, p.name, p.bedrooms, p.showers, p.noise_level, p.rent, p.folder FROM Properties p JOIN SavedProperties sp ON sp.property_id=p.id JOIN Users u ON sp.user_id = u.id WHERE u.session_token=%s ORDER BY id asc;", (session_token,))
    properties = cursor.fetchall()
    
    if len(properties) == 0:
        return []

    # Gets the ids of the properties
    property_ids = []
    for property in properties:
        property_ids.append(property["id"])

    # Creates a list of %s,%s,%s... for the length of the properties
    propertyId_placeholder = ",".join(["%s"] * len(properties))

    # Finds the alt_description of the first image (1.jpg) for each of the saved properties
    cursor.execute("SELECT alt_description FROM Images WHERE property_id IN ({}) AND image_number=1 ORDER BY property_id asc;".format(propertyId_placeholder), tuple(property_ids))
    descriptions = cursor.fetchall()

    # Adds the description to the properties array
    for i in range(len(properties)):
        properties[i]["alt_description"] = descriptions[i]["alt_description"]

    return properties

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

@router.delete("/all")
async def clear_saved(request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    # Rejects the request if the user isn't logged in
    if session_token == "":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    
    cursor.execute("DELETE FROM SavedProperties WHERE user_id=(SELECT id FROM Users WHERE session_token=%s);", (session_token,))
    db.commit()
    return


@router.delete("/{property_id}")
async def unsave_property(property_id: str, request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    # Rejects the request if the user isn't logged in
    if session_token == "":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    cursor.execute("DELETE FROM SavedProperties WHERE user_id=(SELECT id FROM Users WHERE session_token=%s) AND property_id=%s", (session_token, property_id))
    return

