from django.urls import path,include
from .user_views import UserLogin,UserRegister,UserProfile
from .item_views import item_views,item_detail_views,set_like_to_item_views,add_rating_to_item_views
from .admin_test_views import Test_Recomend_auto
from .recomends_views import Get_Top_Resomend_Views

recomend_urls = [
    path("",Get_Top_Resomend_Views.as_view(),name="top-items")
]

admin_urls = [
    path("recomend/",Test_Recomend_auto.as_view(),name="test-recomends")
]

item_urls = [
    path("",item_views.as_view(),name="set-item"),
    path("<int:id>/",item_detail_views.as_view(),name="get-item"),
    path("<int:id>/like/",set_like_to_item_views.as_view(),name="set-or-remove-like-item"),
    path("<int:id>/rating/",add_rating_to_item_views.as_view(),name="set-rating-to-item")
]


urlpatterns = [
    path("",UserProfile.as_view(),name="user-profile"),
    path("register/",UserRegister.as_view(),name="user-register"),
    path("login/",UserLogin.as_view(),name="user-login"),
    path('item/',include(item_urls)),
    path("admin-t/",include(admin_urls)),
    path("recomend/",include(recomend_urls))
]
