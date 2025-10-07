from .item_control import Items,ItemSerializer
from .models import Item,Rating
from celery import shared_task
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

import redis 


r = redis.Redis(host="localhost",port=6379,db=0)

@shared_task
def set_similar_users(user_id,users):
    # print(users)
    print("TEST 4")
    key = f"user:{user_id}:similar-users"
    r.sadd(key,*users)

@shared_task
def set_like_to_item(uset_id,item_id):
    try:
        user = get_object_or_404(User,id=uset_id)
    except Exception:
        return {"err":f"User with id:{uset_id} does not exists!"}
    return Items(user).like_item(item_id)

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

@shared_task
def set_recomend_tops():
    
    r.delete("top_ids")
    r.delete("top:*")
    
    items = Item.objects.all()
    items_with_ratings = []
    for item in items:
        item_ratings = item.ratings.all().values_list("value",flat=True)
        item_rating = sum(item_ratings) / len(item_ratings) if item_ratings else 0
        items_with_ratings.append({
            "id":item.id,
            "rating":item_rating
        })
    
    r.rpush("top_ids",*[i['id'] for i in items_with_ratings])
    for i in items_with_ratings:
        r.hset(f"top:{i['id']}",mapping=i)
    
    top_items_list = []
    for i in items_with_ratings:
        item = Item.objects.get(id=i["id"])
        item = ItemSerializer(item).data
        item['rating'] = i["rating"]
        print(item)
        top_items_list.append(item)

class Admin_panel:
    is_admin = False
    def __init__(self):
        pass
    def check(self,request:Request):
        user:User = request.user
        if user.is_superuser:
            self.is_admin = True
            return True
        else:
            return False
    def test_sort_items(self):
        if not self.is_admin:
            return False
        set_recomend_tops.delay()
        return True
    def get_top(self):
        if not self.is_admin:
            return False
        top_ids = [ i.decode() for i in r.lrange("top_ids",0,-1)]
        
        result = []
        for i in top_ids:
            item_rating = r.hget(f"top:{i}","rating")
            item_exists = Item.objects.filter(id=i).exists()
            if not item_exists:
                continue
            item = ItemSerializer(Item.objects.get(id=i)).data
            item['rating'] = item_rating
            result.append(item)
        return result
            
        
    
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
    @staticmethod
    def control_set_similar_users(user_id,users):
        print("TEST 3")
        set_similar_users.delay(user_id,users)
        return True
        
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
    def control_set_like_to_item(self,item_id):
        user_id = self.request.user.id
        task = set_like_to_item.delay(user_id,item_id)
        key = f"user:{user_id}:tasks"
        
        r.sadd(key,task.id)
        r.expire(key,3600)
        
        return self.RESULT("Ваш запрос в обработке!")
    