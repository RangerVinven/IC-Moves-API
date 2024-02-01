from pydantic import BaseModel
from typing import Optional

class User_Email_Password(BaseModel):
    email: str
    password: str

class User_Email_Password_Fields_Optional(BaseModel):
    email: str | None = None
    password: str | None = None