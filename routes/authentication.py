from fastapi import APIRouter, Response, Request, status
from fastapi.responses import RedirectResponse

from utils.database_connector import cursor, db
from utils.authentication import sha256, generate_session_token, get_session_token_from_request

from models.Users import User_Email_Password

router = APIRouter()

@router.post("/login")
async def login(credentials: User_Email_Password, response: Response):
    credentials.password = sha256(credentials.password)

    # Gets a list of users matching the credentials
    cursor.execute("SELECT id FROM Users WHERE email=%s AND password=%s;", (credentials.email, credentials.password))
    users = cursor.fetchall()

    # Returns 401 if the credentials aren't correct
    if len(users) == 0:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    # Logs the user in
    session_token = generate_session_token(credentials)

    cursor.execute("UPDATE Users SET session_token=%s WHERE email=%s AND password=%s",
                   (session_token, credentials.email, credentials.password))
    db.commit()

    return {
        "token": session_token
    }

@router.get("/logout")
async def logout(request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    # If the user isn't logged in (no session token), redirects to "/"
    if session_token == "":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    # Removes the session token from the database
    cursor.execute("UPDATE Users SET session_token=null WHERE session_token=%s", (session_token,))
    db.commit()

    # Tells the browser to delete the session_token cookie
    return