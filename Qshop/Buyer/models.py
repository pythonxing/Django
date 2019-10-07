from django.db import models
from Seller.models import LoginUser
from django.db.models import Manager

class PayOrder(models.Model):
    order_number = models.CharField(max_length=32)
    order_data = models.DateTimeField(auto_now=True)

    order_total = models.FloatField(blank=True,null=True)
    order_user = models.ForeignKey(to=LoginUser,on_delete=models.CASCADE)

class OrderInfo(models.Model):
    """
    订单详情表
    """
    order_id = models.ForeignKey(to=PayOrder,on_delete=models.CASCADE)
    goods_id = models.IntegerField()
    goods_picture = models.CharField(max_length=32)
    goods_name = models.CharField(max_length=32)
    goods_count = models.IntegerField()
    goods_price = models.FloatField()
    goods_total_price = models.FloatField()
    order_status = models.IntegerField(default=0)
    store_id = models.ForeignKey(to=LoginUser,on_delete=models.CASCADE)

class CartManage(Manager):
    def adds(self,id):
        cart = Cart.objects.get(id=id)
        cart.goods_numbebr += 1
        cart.goods_total += cart.goods_price
        cart.save()

class Cart(models.Model):
    goods_name = models.CharField(max_length=32)
    goods_number = models.IntegerField()
    goods_price = models.FloatField()
    goods_picture = models.CharField(max_length=32)
    goods_total = models.FloatField()
    goods_id = models.IntegerField()
    cart_user = models.IntegerField()

    objects = CartManage()
# Create your models here.