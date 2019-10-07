from django.db import models


class LoginUser(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=32)

    username = models.CharField(max_length=32, null=True, blank=True)
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=32, null=True, blank=True)
    adress = models.TextField(null=True, blank=True)
    User_type = models.IntegerField(default=0)  # 用户0  商家 1  管理员2


class Valid_Code(models.Model):
    code_content = models.CharField(max_length=32)
    code_user = models.EmailField()
    code_time = models.DateTimeField(auto_now=True)
    code_state = models.IntegerField(default=0)


class GoodsType(models.Model):
    goods_type = models.CharField(max_length=32)
    goods_description = models.TextField()
    picture = models.ImageField(upload_to="buyer/images", default="buyer/images/banner05.jpg")


class Goods(models.Model):
    goods_number = models.CharField(max_length=32)
    goods_name = models.CharField(max_length=32)
    goods_price = models.FloatField()
    goods_count = models.IntegerField()
    goods_location = models.CharField(max_length=32)
    goods_safe_date = models.IntegerField()
    goods_pro_time = models.DateField(auto_now=True)
    goods_status = models.IntegerField()
    goods_description = models.TextField(default="好吃还不贵")

    picture = models.ImageField(upload_to='seller/imgs')
    goods_type = models.ForeignKey(to=GoodsType, on_delete=models.CASCADE, default=1)
    goods_store = models.ForeignKey(to=LoginUser, on_delete=models.CASCADE, default=1)

# Create your models here.