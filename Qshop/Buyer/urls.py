from django.urls import path,re_path
from Buyer.views import *
urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    path('goods_list/',goods_list),
    re_path('goods_detail/(?P<id>\d+)/',goods_detail),
]