from ninja import Schema,File
from typing import Optional
from ninja.orm import create_schema
from .models import User
from uuid import UUID


class SignUpSchema(Schema):
    name: str
    email: str
    date_of_birth: str
    phone_number: str
    address: str
    gender: str
    password: str
    profile_picture: Optional[str] = File(None) 


class LoginSchema(Schema):
    email: str
    password: str

class LoginResponseSchema(Schema):
    refresh: str
    access: str

class LogOutResponseSchema(Schema):
    success: bool
    message: str

class ProfileSchema(Schema):
    id: UUID
    name: str
    email: str
    phone_number: str
    date_of_birth: str
    address: str
    gender: str
    profile_picture: str 
   

class DelUserSchema(Schema):
    success: bool
    user: ProfileSchema

class ProfileUpdateResSchema(Schema):
    success: bool
    name: str
    email: str
    phone_number: str
    date_of_birth: str
    address: str
    gender: str
    profile_picture: Optional[str] = File(None) 
    

class ProfileUpdateSchema(Schema):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    gender: Optional[str] = None
    profile_picture: Optional[str] = None

    