from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    account_name: str = Field(..., min_length=3, max_length=256)
    password: str = Field(..., min_length=8, max_length=256)


class LoginRequest(BaseModel):
    account_name: str
    password: str


class AccountResponse(BaseModel):
    id: str
    account_name: str

    class Config:
        from_attributes = True
