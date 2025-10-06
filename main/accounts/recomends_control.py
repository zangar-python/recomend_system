import redis
# from rest_framework.request import Request
from .users_control import Users,User
from .models import Item,Rating
from .item_control import ItemSerializer
from django.shortcuts import get_object_or_404
from rest_framework.serializers import ModelSerializer
from django.db.models.manager import BaseManager

# import numpy as np

r = redis.Redis()

class Recomend_control(Users):
    def __init__(self,request):
        super().setuser(request.user)
        pass
    
    
    def get_top_items(self):
        items_id = [i.decode() for  i in r.lrange("top_ids",0,-1)]
        
        items = Item.objects.filter(id__in=items_id)
        result = []
        items_serialized = ItemSerializer(items,many=True).data
        
        for item in items_serialized:
            item_rating = r.hget(f"top:{item['id']}","rating")
            item['rating'] = item_rating
            result.append(item)
        result.sort(key=lambda x:float(x['rating']),reverse=True)
        return result
    
    # def user_cosine_simular(self,user1,user2):
    #     cosine_simular = np.dot(user1,user2) / (np.linalg.norm(user1) * np.linalg.norm(user2))
    #     return f"Косинусное сходство {cosine_simular:.3f} "
    
    def recomend_item_by_user(self,user_id):
        user = get_object_or_404(User,id=user_id)
        
        r1_key = f"user:{user.id}:recomend"
        for_u_key = f"user:{user.id}:for-you"
        # like_key = f"user:{user.id}:like"
        
        b_liked_key = f"user:{user.id}:liked"
        b_ranked_key = f"user:{user.id}:ranked"
        
        
        exists1 = r.exists(r1_key)
        exists2 = r.exists(for_u_key)
        exists3 = r.exists(b_liked_key)
        
        
        # if exists1 or exists2 or exists3:
        #     return 
        
        owr_users_ranged_it = []
        user_ranged_items = []
        
        if not exists1:
            r.delete(r1_key)
            
            user_ranged_items = Rating.objects.filter(user=user,value__gte=4).order_by("-added_at")[:10].values_list("item",flat=True)
            if not user_ranged_items.exists():
                return {
                    "top":self.get_top_items(),
                    "by_liked_items":self.item_recomend_by_likes(user)
                }
        
            owr_users_ranged_it = Rating.objects.filter(item__in=user_ranged_items,value__gte=4).exclude(user=user).values_list("user",flat=True)
            owr_ratinged_items_id = Rating.objects.filter(user__in=owr_users_ranged_it,value__gte=4).exclude(item__in=user_ranged_items).values_list("item",flat=True)
            recomend_items = Item.objects.filter(id__in=owr_ratinged_items_id).distinct().order_by("-created_at")[:10]
            
            r.rpush(r1_key,*[i.id for i in recomend_items])
            r.expire(r1_key,3600)
        else:
            r_1 = [i.decode() for i in r.lrange(r1_key,0,-1)]
            recomend_items = Item.objects.filter(id__in=r_1).distinct().order_by("-created_at")
        if not exists2:
            r.delete(for_u_key)
            
            liked_items = Item.objects.filter(likes__in=owr_users_ranged_it).exclude(id__in=user_ranged_items).distinct().order_by("-created_at")[:10]
            r.rpush(for_u_key,*[i.id for i in liked_items])
            r.expire(for_u_key,3600)
        else:
            for_u = [i.decode() for i in r.lrange(for_u_key,0,-1)]
            liked_items = Item.objects.filter(id__in=for_u).distinct().order_by("-created_at")          
        if not exists3:
            r.delete(b_liked_key)
            r.delete(b_ranked_key)
            
            by_liked_items = self.item_recomend_by_likes(user)
            
            b_liked = by_liked_items['liked_items_recomend'][:10]
            b_ranked = by_liked_items['ranked_items_recomend'][:10]
            r.rpush(b_liked_key,*[i['id'] for i in b_liked])
            r.expire(b_liked_key,3600)
            r.rpush(b_ranked_key,*[i['id'] for i in b_ranked])
            r.expire(b_ranked_key,3600)
        else:
            b_liked_id = [ i.decode() for i in r.lrange(b_liked_key,0,-1)]
            b_ranked_id = [ i.decode() for i in r.lrange(b_ranked_key,0,-1)]
            
            b_liked = ItemSerializer(Item.objects.filter(id__in=b_liked_id).distinct().order_by("-created_at"),many=True).data
            b_ranked = ItemSerializer(Item.objects.filter(id__in=b_ranked_id).distinct().order_by("-created_at"),many=True).data
        
        # return RatingSerializer(owr_ratinged_items_id,many=True).data
        return {
            "recomend":ItemSerializer(recomend_items,many=True).data,
            "for_you":ItemSerializer(liked_items,many=True).data,
            "by_liked_items":{
                "liked_items_recomend":b_liked,
                "ranked_items_recomend":b_ranked
            }
        }
        # return owr_ratinged_items_id
    def item_recomend_by_likes(self,user:User):
        liked_items:BaseManager[Item] = user.likes.all()
        
        if not liked_items.exists():
            return {
                "liked_items_recomend":[],
                "ranked_items_recomend":[]
            }
        
        users_likes_it = User.objects.filter(likes__in=liked_items)
        liked_items_recomend:BaseManager[Item] = Item.objects.filter(likes__in=users_likes_it).exclude(id__in=liked_items.values_list("id",flat=True)).order_by("-created_at")
        # users_likes_it.likes.all().exclude(liked_items).order_by("-created-at")
        id_items_ranked = Rating.objects.filter(user__in=users_likes_it).exclude(item__in=liked_items)
        ranked_items_recomend = Item.objects.filter(id__in=id_items_ranked).order_by("-created_at")
        
        return {
            "liked_items_recomend":ItemSerializer(liked_items_recomend,many=True).data,
            "ranked_items_recomend":ItemSerializer(ranked_items_recomend,many=True).data
        }
        
        
class RatingSerializer(ModelSerializer):
    class Meta:
        model = Rating
        fields = "__all__"