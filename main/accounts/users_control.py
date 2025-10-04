from django.contrib.auth.models import User
from rest_framework.request import Request
from rest_framework.authtoken.models import Token
from rest_framework.authentication import authenticate
from rest_framework.serializers import ModelSerializer
import redis
from celery.result import AsyncResult

r = redis.Redis()


class Users:
    user = None
    token_key = None
    def __init__(self):
        pass
    
    def RESULT(self,data,error:bool=False):
        if not self.user:
            user_data = None
        user_data = {
            "user":UserSerializer(self.user).data,
            "token":self.token_key
        }
        return {
            "user_data":user_data,
            "data":data,
            "error":error
        }
    def setuser(self,user:User):
        self.user = user
        self.token_key = Token.objects.get_or_create(user=user)[0].key
    def get_user(self):
        key = f"user:{self.user.id}:tasks"
        tasks_id = [i.decode() for i in r.smembers(key)]
        
        tasks_result = []
        for id in tasks_id:
            task = AsyncResult(id)
            if not task.ready():
                tasks_result.append({
                    "task_id":id,
                    "result":"Обработка еще не завершено"
                })
            tasks_result.append(task.result)
        return self.RESULT({
            "data":"Ваш профиль",
            "tasks":tasks_result
        })
    
    
    def register_user(self,request:Request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email","")
        if not username or not password:
            return self.RESULT("Введит поля username / password!",True)
        if User.objects.filter(username=username).exists():
            return self.RESULT(f"Пользователь с таким именем {username} уже существует",True)
        user = User.objects.create_user(username,email,password)
        self.setuser(user)
        return self.RESULT("Вы успешно зарегестрировались")
    
    def login_user(self,request:Request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return self.RESULT("Введит поля username / password",True)
        user = authenticate(username=username,password=password)
        if not user:
            return self.RESULT("Пользователь с такими данными не существует!",True)
        self.setuser(user)
        return self.RESULT("Вы залогинились")

class UserProfile(Users):
    def __init__(self):
        super().__init__()
    



class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username','email','id']