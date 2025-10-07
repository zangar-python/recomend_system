from django.contrib.auth.models import User
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer
from .users_control import Users,UserSerializer
from .models import Item,Rating
from django.shortcuts import get_object_or_404

from django.db.models.manager import BaseManager
from django.db.models import Count,Prefetch

class Items(Users):
    def __init__(self,user:User):
        super().setuser(user)
        pass
    
    def get_users(self):
        users = User.objects.prefetch_related("likes")
        users_likes = User.objects.prefetch_related("likes").values_list("likes","username")
        obj = []
        
        
        for likes in users_likes:
            
            obj.append({
                "user_likes":likes[0],
                "username":likes[1]
            })
        # user_list = list(users)
        # for user in user_list:
        #     user.liked_items = user.likes.all().values_list("id",flat=True)
        return {
            "users":UserSerializer(users,many=True).data,
            "users_likes":obj
        }
    
    def get_items_one_sql(self):
        items = Item.objects.select_related("author").prefetch_related("likes").annotate(likes_count=Count("likes")).filter(likes_count__gt=1)
        return ItemSerializer(items,many=True).data
    
    def set_item(self,title,text):
        # if not title or not text:
        #     return self.RESULT("Заполните поля title / text",True)
        author = self.user
        Item.objects.create(
            title=title,
            text=text,
            author=author
        )
        # return self.RESULT({
        #     "item":ItemSerializer(item).data,
        #     "created":True
        # })
        return
    def get_item(self,id):
        item = get_object_or_404(Item,id=id)
        ratings:list[int] = item.ratings.all().values_list("value",flat=True)
        
        
        return self.RESULT({
            "item":ItemSerializer(item).data,
            "likes_count":item.likes.count(),
            "rating":sum(ratings) / len(ratings) if ratings else 0
        })
    def like_item(self,id):
        user =self.user
        try:
            item = get_object_or_404(Item,id=id)
        except Exception:
            return self.RESULT({"err":f"Item with id:{id} is does not exists"},True)
        if not item.likes.filter(id=user.id).exists():
            item.likes.add(user)
            return self.RESULT(f"Лайк поставлен likes = {item.likes.count()}")
        else:
            item.likes.remove(user)
            return self.RESULT(f"Лайк убран likes = {item.likes.count()}")
    
    def item_set_rating(self,item,value):
        if item.author.id == self.user.id:
            return self.RESULT("Вы не можете оставить оценку на свой же товар",True)
        if self.user.ratings.filter(item=item).exists():
            # return self.RESULT("Вы уже поставили свой",True)
            rating:Rating = self.user.ratings.get(item=item)
            rating.value = value
            rating.save()
        else:
            rating = Rating.objects.create(
                user=self.user,
                item=item,
                value=value
            )
        return self.RESULT(
            {
                "added":True,
                "to":ItemSerializer(item).data,
                "rating":RatingSerializer(rating).data
            }
        )
    def user_items_get(self):
        my_items = ItemSerializer(Item.objects.select_related("author").filter(author__id=self.user.id),many=True).data
        return self.RESULT({
            "my_items":my_items
        })
        
    
class ItemSerializer(ModelSerializer):
    class Meta:
        model = Item
        fields = ['author','title','text','id']

        
    
class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"