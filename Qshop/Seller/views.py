from django.shortcuts import render,HttpResponseRedirect,HttpResponse
from Seller.models import *
import hashlib
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
        if email:
        #首先检测email有没有
            user = LoginUser.objects.filter(email=email).first()
            if user:
                db_password = user.password
                password = setPassword(password)
                if db_password == password:
                    response = HttpResponseRedirect('/Seller/index/')
                    response.set_cookie('username',user.email)
                    response.set_cookie('user_id',user.id)
                    request.session['username'] = user.email
                    return response
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

# Create your views here.