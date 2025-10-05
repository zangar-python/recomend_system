import redis
# from rest_framework.request import Request
from .users_control import Users
from .models import Item
from .item_control import ItemSerializer

r = redis.Redis()

class Recomend_control(Users):
    def __init__(self,request):
        super().setuser(request.user)
        pass
    
    
    def get_top_items(self):
        items_id = [i.decode() for  i in r.lrange("top_ids",0,-1)]
        
        result = []
        for i in items_id:
            item_rating = r.hget(f"top:{i}","rating")
            if not Item.objects.filter(id=i).exists():
                continue
            item = ItemSerializer(Item.objects.get(id=i)).data
            item['rating'] = item_rating
            result.append(item)
        return self.RESULT({"tops":result})