from pydantic import BaseModel

class User_Email_Password(BaseModel):
    email: str
    password: str