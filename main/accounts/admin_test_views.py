from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from .tasks import Admin_panel

class Test_Recomend_auto(APIView):
    permission_classes = [IsAdminUser]
    def post(self,request:Request):
        admin_test = Admin_panel()
        admin_test.check(request)
        return Response(admin_test.test_sort_items())
    def get(self,request:Request):
        admin_test = Admin_panel()
        admin_test.check(request)
        return Response({"res":admin_test.get_top()})