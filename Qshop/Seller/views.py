import json
import hashlib
import requests
import time,datetime
from Seller.models import *
from Qshop.settings import DING_URL
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,HttpResponseRedirect,HttpResponse


def LoginValid(fun):
    def inner(request,*args,**kwargs):
        cookie_username = request.COOKIES.get('username')
        session_username = request.session.get('username')
        if cookie_username and session_username and cookie_username==session_username:
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect('/Seller/login/')
    return inner
def setPassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result
def register(request):
    error_message = ''
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email:
        #首先检测email有没有
            user = LoginUser.objects.filter(email=email).first()
            if not user:
                new_user = LoginUser()
                new_user.email = email
                new_user.password = setPassword(password)
                new_user.save()
            else:
                error_message = '邮箱已经被注册'
        else:
            error_message = '邮箱不可以为空'
    return render(request,'seller/register.html',locals())

def login(request):
    error_message = ''
    if request.method == 'POST':
        email = request.POST.get('email')#从前端获取输入的email
        password = request.POST.get('password')#从前端获取输入的password
        code = request.POST.get("valid_code")#从前端获取输入的验证码   通过name属性
        if email:
        #首先检测email有没有
            user = LoginUser.objects.filter(email=email).first()
            if user:
                db_password = user.password
                password = setPassword(password)
                if db_password == password:
                    #检测验证码
                    #获取验证码
                    codes = Valid_Code.objects.filter(code_user=email).order_by("-code_time").first()
                    #校验验证码是否存在，是否过期，是否被使用
                    now = time.mktime(datetime.datetime.now().timetuple())
                    db_time = time.mktime(codes.code_time.timetuple())
                    t = (now - db_time) / 60
                    if codes and codes.code_state == 0 and t <= 5 and codes.code_content.upper() == code.upper():
                        response = HttpResponseRedirect('/Seller/index/')
                        response.set_cookie('username',user.email)
                        response.set_cookie('user_id',user.id)
                        request.session['username'] = user.email
                        return response
                    else:
                        error_message = "验证码错误"
                else:
                    error_message = '密码错误'
            else:
                error_message = '用户不存在'
        else:
            error_message = '邮箱不可以为空'
    return render(request,'seller/login.html',locals())
@LoginValid
def index(request):
    return render(request,'seller/index.html',locals())

@LoginValid
def add_goods(request):
    goods_type_list = GoodsType.objects.all()
    if request.method == "POST":
        data = request.POST
        file = request.FILES

        goods = Goods()
        goods.goods_number = data.get("goods_number")
        goods.goods_name = data.get("goods_name")
        goods.goods_price = float(data.get("goods_price"))
        goods.goods_count = int(data.get("goods_count"))
        goods.goods_location = data.get("goods_location")
        goods.goods_safe_date = int(data.get("goods_safe_date"))
        goods.goods_pro_time = data.get("goods_pro_time")
        goods.goods_status = 1
        #保存外键类型
        goods.goods_type = GoodsType.objects.get(id = int(data.get("goods_type")))
        #保存图片
        goods.picture = file.get("picture")
        #保存对应的卖家
        user_id = request.COOKIES.get("user_id")
        goods.goods_store = LoginUser.objects.get(id = int(user_id))

        goods.save()
    return render(request,'seller/add_goods.html',locals())

@LoginValid
def goods_list(request,status,page=1):
    user_id = request.COOKIES.get("user_id")
    user = LoginUser.objects.get(id = int(user_id))
    page = int(page)
    if status == '1':
        goodses = Goods.objects.filter(goods_store=user,goods_status=1)
    elif status == '0':
        goodses = Goods.objects.filter(goods_store=user,goods_status=0)
    else:
        goodses = Goods.objects.all()
    # 卖家页面分页功能
    all_goods = Paginator(goodses,10)
    goods_list = all_goods.page(page)
    return render(request,'seller/goods_list.html',locals())

def sendDing(content,to=None):
    """
    使用dingding机器人发送验证码
    :param content:
    :param to:
    :return:
    """
    headers = {
        "Content-Type":"application/json",
        "Charset":"utf-8"
    }
    request_data = {
        "msgtype":"text",
        "text":{
            "content":content
        },
        "at":{
            "atMobiles":[
            ],
            "isAtAll":True
        }
    }
    if to:
        request_data["at"]["atMobiles"].append(to)
        request_data["at"]["isAtAll"] = False
    else:
        request_data["at"]["atMobiles"].clear()
        request_data["at"]["isAtAll"] = True
    sendData = json.dumps(request_data)
    response = requests.post(url=DING_URL,headers=headers,data=sendData)
    content = response.json()
    return content

import random
def random_code(len=6):
    """
    生成六位验证码
    :param len:
    :return:
    """
    string = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    valid_code = "".join([random.choice(string) for i in range(len)])
    return valid_code
@csrf_exempt
def send_login_code(request):
    result = {
        "code":200,
        "data":""
    }
    if request.method == "POST":
        email = request.POST.get("email")
        code = random_code()
        c = Valid_Code()
        c.code_user = email
        c.code_content = code
        c.save()
        send_data = "%s的验证码是%s,请不要告诉别人"%(email,code)
        sendDing(send_data)#发送验证码
        result["data"] = "发送成功"
    else:
        result["code"] = 400
        result["data"] = "发送失败"
    return JsonResponse(result)

# Create your views here.