import hashlib
import time,datetime
from Buyer.models import *
from Seller.models import *
from alipay import AliPay
from Seller.views import setPassword
from django.http import JsonResponse
from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from Qshop.settings import alipay_public_key_string,alipay_private_key_string
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



@LoginValid
def add_cart(request):
    result = {
        "code":200,
        "data":""
    }
    if request.method == "POST":
        id = int(request.POST.get("goods_id"))
        count = int(request.POST.get("count",1))

        goods = Goods.objects.get(id=id)#获取商品信息
        cart = Cart()
        cart.goods_name = goods.goods_name
        cart.goods_number = count
        cart.goods_price = goods.goods_price
        cart.goods_picture = goods.picture
        cart.goods_total = goods.goods_price*count
        cart.goods_id = id
        cart.cart_user = request.COOKIES.get("user_id")
        cart.save()
        result["data"] = "加入购物车成功"
    else:
        result["code"] = 500
        result["data"] = "请求方式错误"
    return JsonResponse(result)

def cart(request):
    user_id = request.COOKIES.get("user_id")
    goods = Cart.objects.filter(cart_user=int(user_id))
    count = goods.count()
    return render(request,"buyer/cart.html",locals())


@LoginValid
def pay_order(request):
    goods_id = request.GET.get("goods_id")
    count = request.GET.get("count")
    if goods_id and count:
        # 保存订单表，保存总价
        order = PayOrder()
        order.order_number = str(time.time()).replace(".", "")
        order.order_data = datetime.datetime.now()
        order.order_user = LoginUser.objects.get(id=int(request.COOKIES.get("user_id")))  # 订单对应的买家
        order.save()
        # 保存订单详情
        # 查询商品的信息
        goods = Goods.objects.get(id=int(goods_id))
        order_info = OrderInfo()
        order_info.goods_id = goods_id
        order_info.goods_picture = goods.picture
        order_info.goods_name = goods.goods_name
        order_info.goods_count = int(count)
        order_info.goods_price = goods.goods_price
        order_info.goods_total_price = goods.goods_price * int(count)
        order_info.store_id = goods.goods_store
        order_info.save()
        order.order_total = order_info.goods_total_price
        order.save()
    return render(request, "buyer/pay_order.html", locals())


@LoginValid
def pay_order_more(request):
    data = request.GET
    data_item = data.items()
    request_data = []
    for key, value in data_item:
        if key.startswith("check_"):
            goods_id = key.split("_", 1)[1]
            count = data.get("count_" + goods_id)
            request_data.append((int(goods_id), int(count)))
    if request_data:
        # 保存订单表，但是保存总价
        order = PayOrder()
        order.order_number = str(time.time()).replace(".", "")
        order.order_data = datetime.datetime.now()
        order.order_user = LoginUser.objects.get(id=int(request.COOKIES.get("user_id")))
        order.save()
        # 保存订单详情
        # 查询商品的信息
        order_total = 0
        for goods_id, count in request_data:
            print(goods_id, count)
            goods = Goods.objects.get(id=int(goods_id))

            order_info = OrderInfo()
            order_info.order_id = order
            order_info.goods_id = goods_id
            order_info.goods_picture = goods.picture
            order_info.goods_name = goods.goods_name
            order_info.goods_count = int(count)
            order_info.goods_price = goods.goods_price
            order_info.goods_total_price = goods.goods_price*int(count)
            order_info.store_id = goods.goods_store#商品卖家，goods.good_store本身就是一条卖家信息
            order_info.save()
            order_total += order_info.goods_total_price
        order.order_total = order_total
        order.save()
    return render(request, 'buyer/pay_order.html', locals())


def AliPayViews(request):
    order_number = request.GET.get("order_number")
    order_total = request.GET.get("order_total")
    # 实例化支付
    alipay = AliPay(
        appid="2016101200667752",
        app_notify_url=None,
        app_private_key_string=alipay_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2"
    )

    # 实例化订单
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_number,  # 订单号
        total_amount=str(order_total),  # 支付金额  字符串
        subject="生鲜交易",  # 支付主题
        return_url="http://127.0.0.1:8000/Buyer/pay_result/",
        notify_url="http://127.0.0.1:8000/Buyer/pay_result/"
    )  # 网页支付订单
    result = "https://openapi.alipaydev.com/gateway.do?" + order_string
    return HttpResponseRedirect(result)


def pay_result(request):
    out_trade_no = request.GET.get("out_trade_no")
    if out_trade_no:
        order = PayOrder.objects.get(order_number=out_trade_no)
        order.order_status = 1
        order.save()
    return render(request, 'buyer/pay_result.html', locals())

# Create your views here.