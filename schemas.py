from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class PostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=280)
    location: str | None = None

class PostOut(BaseModel):
    id: int
    content: str
    location: str | None
    owner_id: int

    model_config = {"from_attributes": True}
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}
