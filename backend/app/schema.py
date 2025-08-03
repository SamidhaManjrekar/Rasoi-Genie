# schema.py - CORRECTED VERSION
from pydantic import BaseModel, EmailStr
from typing import List

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class PreferenceCreate(BaseModel):  # Renamed from PreferencesBase/Create
    diet_type: str
    cuisine: List[str]
    meals: List[str]
    cooking_time: str  # Changed from cook_time to cooking_time
    health_conditions: List[str]

class PreferenceResponse(PreferenceCreate):  # Renamed from PreferencesResponse
    class Config:
        from_attributes = True  # Updated for Pydantic v2