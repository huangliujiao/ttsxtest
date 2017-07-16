#coding=utf-8
from django.db import models
from tinymce.models import HTMLField
# Create your models here.
class UserInfo(models.Model):
    uname = models.CharField(max_length=20)
    upwd =  models.CharField(max_length=40)
    umail = models.CharField(max_length=20)
    ushou = models.CharField(max_length=30)
    uaddress = models.CharField(max_length=100)
    ucode = models.CharField(max_length=10)
    uphone = models.CharField(max_length=20)

# Create your models here.
class TypeInfo(models.Model):
    ttitle=models.CharField(max_length=10)
    isDelete=models.BooleanField(default=False)

    def __str__(self):
        return self.ttitle

class GoodsInfo(models.Model):
    gtitle=models.CharField(max_length=20)
    gpic=models.ImageField(upload_to='goods/')
    gprice=models.DecimalField(max_digits=5,decimal_places=2)
    gclick=models.IntegerField()
    gunit=models.CharField(max_length=10)
    isDelete = models.BooleanField(default=False)
    gsubtitle=models.CharField(max_length=200)
    gkucun = models.IntegerField(default=100)
    gcontent=HTMLField()
    gtype=models.ForeignKey('TypeInfo')

class CartInfo(models.Model):
    goods=models.ForeignKey(GoodsInfo)
    user=models.ForeignKey(UserInfo)
    count=models.IntegerField()

class OrderMain(models.Model):
    orderid=models.CharField(max_length=20,primary_key=True)#20170713000000用户id
    order_time=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(UserInfo)
    total=models.DecimalField(max_digits=8,decimal_places=2,default=0)
    state=models.IntegerField(default=0)

class OrderDetail(models.Model):
    order=models.ForeignKey(OrderMain)
    goods=models.ForeignKey(GoodsInfo)
    count=models.IntegerField()
    price=models.DecimalField(max_digits=5,decimal_places=2)
