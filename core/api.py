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
from ninja.responses import Response
from rest_framework.authtoken.models import Token


User = get_user_model()

router = Router()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
            try:
                token_obj = Token.objects.get(key=token)
                user = token_obj.user
                return user
            except Token.DoesNotExist:
                return None 
  


@router.post("/signup", response={201: ProfileSchema, 400: str})
def signup(request, payload: SignUpSchema, profile_picture: UploadedFile = File(...)):
    print(payload)
    if User.objects.filter(email=payload.email).exists():
        return 400, "User with this email already exists."
    user_data = payload.dict()
    print(user_data)
    hashed_password = make_password(user_data.get('password'))
    user_data["password"] = hashed_password
    user = User.objects.create(**user_data)
    user.profile_picture.save(profile_picture.name, profile_picture)
    user.is_active = True
    Token.objects.get_or_create(user=user)
    user.save()
    return 201, ProfileSchema.from_orm(user)

    

@router.post("/login", response={200: LoginResponseSchema, 401: str})
def login(request, payload: LoginSchema):
    user = authenticate(request, email=payload.email, password=payload.password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return {
            'token': str(token),
            'name': user.name,
            'email': user.email
        }
    return Response({"message": "Invalid Login Credentials"}, status=404)



@router.get("/user{user_id}", auth=AuthBearer(), response={201: ProfileSchema, 404: str})
def get_user(request,  user_id: UUID):
    user = get_object_or_404(User, id=user_id)
    return 201, user


    
@router.put("/user/{user_id}", auth=AuthBearer(), response={200: ProfileSchema, 404: str})
def update_user(request, user_id: UUID, payload: ProfileUpdateSchema):
    authenticated_user = request.auth
    if authenticated_user.id != user_id:
        return Response({"message": "You Can't Update another persons Profile"}, status=200)
    user = get_object_or_404(User, id=user_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        print(attr, value)
        setattr(user, attr, value)
    user.save()
    return user


@router.delete("/user/{user_id}", auth=AuthBearer(), response={200: DelUserSchema, 404: str})
def delete_user(request, user_id: UUID):
    authenticated_user = request.auth
    if authenticated_user.id != user_id:
        return Response({"message": "You Can't Delete another person's Profile"}, status=200)
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return Response({"message": "Deleted"}, status=200)




@router.post("/logout", response={200: LogOutResponseSchema, 401: str})
def logout_user(request):
    logout(request)
    return {"success": True, "message": "Logout successful"}