from fastapi import APIRouter

from utils.database_connector import cursor, db
from utils.authentication import generate_session_token, sha256

from models.Users import User_Email_Password

router = APIRouter()

# For development only
@router.get("/all")
async def get_users():
    cursor.execute("SELECT * FROM Users;")
    users = cursor.fetchall()

    return users

@router.post("/")
async def create_user(user: User_Email_Password):
    session_token = generate_session_token(user)

    cursor.execute("INSERT INTO Users (email, password, session_token) VALUES (%s, %s, %s);", (user.email, sha256(user.password), session_token))
    db.commit()

    return

