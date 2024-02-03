from time import time
import hashlib

from fastapi import Request
from models.Users import User_Email_Password

from utils.database_connector import cursor

def sha256(string_to_hash):
    return hashlib.sha256(string_to_hash.encode()).hexdigest()

def generate_session_token(user: User_Email_Password):
    return sha256(str(time()) + user.email + user.password)

def get_session_token_from_request(request: Request):
    session_token = request.headers.get("session_token")

    if session_token is None:
        return ""
    else:
        return session_token
    
# Checks if the email doesn't exist in the database
def check_if_email_is_unique(email):
    cursor.execute("SELECT id FROM Users WHERE email=%s;", (email,))
    users = cursor.fetchall()

    if users == []:
        return True
    else:
        return False