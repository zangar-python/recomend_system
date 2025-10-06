from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from .recomends_control import Recomend_control
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

class Get_Top_Resomend_Views(APIView):
    def get(self,request:Request):
        user_set = Recomend_control(request)
        return Response (user_set.get_top_items())
class Get_Recomend_Items_Views(APIView):
    def get(self,request:Request,user_id):
        return Response( Recomend_control(request).recomend_item_by_user(user_id) )

class Get_end_point(APIView):
    def get(self,request:Request,user_id):
        return Response(Recomend_control(request).endpoint_recomend_get(user=get_object_or_404(User,id=user_id)))