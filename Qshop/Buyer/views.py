import hashlib
import time,datetime
from Buyer.models import *
from Seller.models import *
from Seller.views import setPassword
from django.http import JsonResponse
from django.shortcuts import render,HttpResponseRedirect,HttpResponse
def LoginValid(fun):
    def inner(request,*args,**kwargs):
        cookie_user = request.COOKIES.get("username")
        session_user = request.session.get("username")
        if cookie_user and session_user and cookie_user == session_user:
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect("Buyer/login/")
    return inner
def register(request):
    if request.method == 'POST':
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        db_password = request.POST.get('cpwd')
        if password == db_password:
            user = LoginUser()
            user.username = username
            user.password = setPassword(password)
            user.email = email
            user.save()
            return HttpResponseRedirect('/Buyer/login/')
    return render(request,'buyer/register.html',locals())
def login(request):
    if request.method == "POST":
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        user = LoginUser.objects.filter(email=email).first()
        if user:
            db_password = user.password
            password = setPassword(password)
            if db_password == password:
                response = HttpResponseRedirect('/Buyer/index/')
                response.set_cookie('username',user.username)
                response.set_cookie('user_id',user.id)
                response.set_cookie('email',user.email)
                request.session['username'] = user.username
                return response
    return render(request,'buyer/login.html',locals())
def index(request):
    goods_type = GoodsType.objects.all()
    result = []
    for ty in goods_type:
        goods = ty.goods_set.order_by("-goods_pro_time")
        if len(goods)>4:
            goods = goods[:4]
            result.append({"type":ty,"goods_list":goods})
            print(result)
    return render(request,'buyer/index.html',locals())

def goods_list(request):
    request_type = request.GET.get("type")
    keyword = request.GET.get("keywords")
    goods_list = []
    if request_type == "t":
        if keyword:
            id = int(keyword)
            goods_type = GoodsType.objects.get(id = id)
            goods_list = goods_type.goods_set.order_by("-goods_pro_time")
    elif  request_type == "k":
        if keyword:
            goods_list = Goods.objects.filter(goods_name__contains=keyword).order_by("-goods_pro_time")
    #买家页面分页功能
    if goods_list:
        lenth = len(goods_list) / 5
        if lenth != int(lenth):
            lenth += 1
        lenth = int(lenth)
        recommend = goods_list[:lenth]
    return render(request,"buyer/goods_list.html",locals())

def goods_detail(request,id):
    goods = Goods.objects.get(id = int(id))
    return render(request,"buyer/detail.html",locals())

@LoginValid
def user_info(request):
    return render(request,"buyer/user_info.html",locals())
# @LoginValid
# def pay_order(request):
#     goods_id = request.GET.get("goods_id")
#     count = request.GET.get("count")
#     if goods_id and count:
#         #保存订单表，保存总价
#         order = PayOrder()
#         order.order_number = str(time.time()).replace(".","")
#         order.order_data = datetime.datetime.now()
#         order.order_user = LoginUser.objects.get(id = int(request.COOKIES.get("user_id")))#订单对应的买家
#         order.save()
#         #保存订单详情
#         #查询商品的信息
#         goods = Goods.objects.get(id = int(goods_id))
#         order_info = OrderInfo()
#         order_info.goods_id = goods_id
#         order_info.goods_picture = goods.picture
#         order_info.goods_name = goods.goods_name
#         order_info.goods_count = int(count)
#         order_info.goods_price = goods.goods_price
#         order_info.goods_total_price = goods.goods_price*int(count)
#         order_info.store_id = goods.goods_store
#         order_info.save()
#         order.order_total = order_info.goods_total_price
#         order.save()
#     return render(request,"buyer/pay_order.html",locals())
# @LoginValid
# def pay_order(request):


# Create your views here.