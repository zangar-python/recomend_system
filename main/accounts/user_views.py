from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .users_control import Users
from rest_framework.permissions import AllowAny
from .item_control import Items

class UserRegister(APIView):
    permission_classes = [AllowAny]
    def post(self,request:Request):
        return Response(Users().register_user(request))
class UserLogin(APIView):
    permission_classes = [AllowAny]
    def post(self,request:Request):
        return Response(Users().login_user(request))

class UserProfile(APIView):
    def get(self,request:Request):
        users_control = Users()
        users_control.setuser(request.user)
        return Response(users_control.get_user())
    
class users_get_views(APIView):
    def get(self,request:Request):
        return Response(Items(request.user).get_users())
