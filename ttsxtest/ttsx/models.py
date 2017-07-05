#coding=utf-8
from django.db import models

# Create your models here.
class UserInfo(models.Model):
    uname = models.CharField(max_length=20)
    upwd =  models.CharField(max_length=40)
    umail = models.CharField(max_length=20)
    ushou = models.CharField(max_length=30)
    uaddress = models.CharField(max_length=100)
    ucode = models.CharField(max_length=10)
    uphone = models.CharField(max_length=20)