# Define how data is structured for api calls to the user endpoints
# like what the api returns as a response, how api calls should look, etc


from pydantic import BaseModel, EmailStr

class SignUpRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignUpResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr

    class Config:
        from_attributes = True
