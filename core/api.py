from django.contrib.auth import get_user_model
from ninja.security import django_auth, HttpBearer
from ninja import NinjaAPI, Router, File
from ninja import UploadedFile, File
from .schemas import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from uuid import UUID


User = get_user_model()

router = Router()
  
@router.post("/signup", response={201: ProfileSchema, 400: str})
def signup(request, payload: SignUpSchema, profile_picture: UploadedFile = File(...)):
    print(payload)
    if User.objects.filter(email=payload.email).exists():
        return 400, "User with this email already exists."
    user_data = payload.dict()
    print(user_data)
    #used to hash our password to enhance application security
    hashed_password = make_password(user_data.get('password'))
    user_data["password"] = hashed_password
    user = User.objects.create(**user_data)
    user.profile_picture.save(profile_picture.name, profile_picture)
    return 201, ProfileSchema.from_orm(user)



#retrieves the logged in users Profile
@router.get("/profile", response={200: ProfileSchema, 400: str})
def get_user(request):
       if request.user.is_authenticated:
           user = request.user
       return user

#handling authentication
class GlobalAuth(HttpBearer):
    def authenticate(self, request, token):
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        if user is not None:
            return user
        raise HttpError(401, "Invalid token")
    
    

@router.post("/login", response={200: LoginResponseSchema, 401: str})
def login(request, payload: LoginSchema):
    user = authenticate(request, email=payload.email, password=payload.password)
    if user:
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    return {"error": "Invalid credentials"}, 401
    


@router.post("/logout", response={200: LogOutResponseSchema, 401: str})
def logout_user(request):
    logout(request)
    return {"success": True, "message": "Logout successful"}



@router.put("/user/{user_id}", response={200: ProfileSchema, 404: str})
def update_user(request, user_id: UUID, payload: ProfileUpdateSchema):
    user = get_object_or_404(User, id=user_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        print(attr, value)
        setattr(user, attr, value)
    user.save()
    return user


@router.delete("/user/{user_id}", response={200: DelUserSchema, 404: str})
def delete_user(request, user_id: UUID):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return {"success": True}


