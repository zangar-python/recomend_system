from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from .recomends_control import Recomend_control

class Get_Top_Resomend_Views(APIView):
    def get(self,request:Request):
        user_set = Recomend_control(request)
        return Response (user_set.get_top_items())