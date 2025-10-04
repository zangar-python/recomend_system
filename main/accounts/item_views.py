from .item_control import Items
from .tasks import TasksControl

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

class item_views(APIView):
    def post(self,request:Request):
        return Response(TasksControl(request).control_set_item())
class item_detail_views(APIView):
    def get(self,request:Response,id):
        return Response(Items(request.user).get_item(id))
class add_rating_to_item_views(APIView):
    def post(self,request:Request,id):
        return Response( TasksControl(request).control_set_rating_to_item(id))
class set_like_to_item_views(APIView):
    def post(self,request:Request,id):
        return Response( Items(request.user).like_item(id) )