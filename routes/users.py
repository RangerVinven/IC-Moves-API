from fastapi import APIRouter, Response, Request, status

from utils.database_connector import cursor, db
from utils.authentication import generate_session_token, get_session_token_from_request, sha256, check_if_email_is_unique, validate_email

from models.Users import User_Email_Password_Verify_Password, User_Email_Password_Fields_Optional

router = APIRouter()


# For development only
@router.get("/all")
async def get_users():
    cursor.execute("SELECT * FROM Users;")
    users = cursor.fetchall()

    return users


@router.get("/")
async def get_user(request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    # Ensures the user is logged in
    if session_token == "":
        response.status = status.HTTP_401_UNAUTHORIZED
        return

    cursor.execute("SELECT email FROM Users WHERE session_token=%s;", (session_token,))
    return cursor.fetchone()


@router.post("/")
async def create_user(user: User_Email_Password_Verify_Password, response: Response):
    session_token = generate_session_token(user)

    if user.password != user.verify_password:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return
    
    if not validate_email(user.email):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    
    # Returns true if the email is unique
    if not check_if_email_is_unique(user.email):
        response.status_code = status.HTTP_409_CONFLICT
        return

    cursor.execute("INSERT INTO Users (email, password, session_token) VALUES (%s, %s, %s);",
                   (user.email, sha256(user.password), session_token))
    db.commit()

    return {
        "token": session_token
    }

@router.patch("/")
async def update_user(user: User_Email_Password_Fields_Optional, request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    # Ensures the user is logged in
    if session_token == "":
        response.status = status.HTTP_401_UNAUTHORIZED
        return

    # Ensures the user entered at least an email or password
    if user.email is None and user.password is None:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return
    
    if not (user.email is None):
        if not validate_email(user.email):
            response.status_code = status.HTTP_400_BAD_REQUEST
            return
    
    # Returns true if the email is unique
    if not check_if_email_is_unique(user.email):
        response.status_code = status.HTTP_409_CONFLICT
        return

    # If the user wants to update their email
    if user.password is None:
        cursor.execute("UPDATE Users SET email=%s WHERE session_token=%s;", (user.email, session_token))

    # If the user wants to update their password
    elif user.email is None:
        cursor.execute("UPDATE Users SET password=%s WHERE session_token=%s;", (sha256(user.password), session_token))

    # If the user wants to update both their email and password
    else:
        cursor.execute("UPDATE Users SET email=%s, password=%s WHERE session_token=%s;",
                       (user.email, sha256(user.password), session_token))

    db.commit()
    return

@router.delete("/")
async def delete_user(request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    if session_token == "":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    # Deletes the data about the user from the SavedProperties and Users database
    cursor.execute("DELETE FROM SavedProperties WHERE user_id=(SELECT id FROM Users WHERE session_token=%s);", (session_token,))
    cursor.execute("DELETE FROM Users WHERE session_token=%s;", (session_token,))
    db.commit()

    return