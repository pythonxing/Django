from django.urls import path,re_path
from Buyer.views import *
urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    path('goods_list/',goods_list),
    re_path('goods_detail/(?P<id>\d+)/',goods_detail),
    path('user_info/',user_info),
    path('add_cart/',add_cart),
    path('cart/',cart),
    path('pay_order/',pay_order),
    path('pay_order_more/',pay_order_more),
    path('pay_result/',pay_result),
    path('alipay/',AliPayViews),

]