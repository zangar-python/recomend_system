from .item_control import Items
from .models import Item,Rating
from celery import shared_task
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

import redis 

r = redis.Redis(host="localhost",port=6379,db=0)

@shared_task
def set_rating_to_item(user_id,item_id,value):
    try :
        user = get_object_or_404(User,id=user_id)
        item = get_object_or_404(Item,id=item_id)
        return Items(user).item_set_rating(item,value)
    except Exception as e:
        return f"User and Item with this id {user_id},{item_id} does not exists"
    

@shared_task
def set_item(user_id,title,text):
    try :
        user = get_object_or_404(User,id=user_id)
        return Items(user).set_item(title,text)
    except Exception as e:
        return {"err":f"user with id:{user_id} does not exists"}
    
class TasksControl:
    def __init__(self,request:Request):
        self.request = request
        pass
    def RESULT(self,data,err:bool=False):
        return {
            "user":{
                "username":self.request.user.username,
                "id":self.request.user.id
            },
            "data":data,
            "error":err
        }
    def control_set_rating_to_item(self,id):
        value = self.request.data.get("value")
        if not value:
            return self.RESULT("Введите оценку",True)
        if not isinstance(value,int):
            return self.RESULT("Неправильно введенные данные",True)
        if 1 > value or value > 5:
            return self.RESULT("Оценка не может быть меньше 1 и больше 5",True)
        task = set_rating_to_item.delay(self.request.user.id,id,value)
        
        key = f"user:{self.request.user.id}:tasks"
        
        r.sadd(key,task.id)
        r.expire(key,3600)
        
        return self.RESULT("Ваша оценка в обработке")
    def control_set_item(self):
        title = self.request.data.get("title")
        text = self.request.data.get("text")
        if not title or not text:
            return self.RESULT("Введите данные:title,text.")
        set_item.delay(self.request.user.id,title,text)
        
        return self.RESULT("Ваш запрос в обработке")
        