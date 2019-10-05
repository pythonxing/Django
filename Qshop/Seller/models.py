from django.db import models
class LoginUser(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=32)

    username = models.CharField(max_length=32,null=True,blank=True)
    phone_number = models.CharField(max_length=32,null=True,blank=True)
    age = models.IntegerField(null=True,blank=True)
    gender = models.CharField(max_length = 32,null=True,blank=True)
    adress = models.TextField(null=True,blank=True)
    User_type = models.IntegerField(default=0) #用户0  商家 1  管理员2


class Valid_Code(models.Model):
    code_content = models.CharField(max_length=32)
    code_user = models.EmailField()
    code_time = models.DateTimeField(auto_now=True)
    code_state = models.IntegerField(default=0)
# Create your models here.