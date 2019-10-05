from django.urls import path,re_path
from Seller.views import *

urlpatterns = [
    path('register/',register),
    path('login/',login),
    path('index/',index),
    path('slc/',send_login_code),
]