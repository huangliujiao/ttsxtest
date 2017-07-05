from django.shortcuts import render,redirect
from .models import UserInfo
from django.http import JsonResponse,HttpResponse
from hashlib  import sha1
# Create your views here.
def login(request):
    return render(request,'ttsx/login.html')

def register(request):
    return render(request,'ttsx/register.html')

def register_check(request):
    user_name=request.POST.get('user_name')
    pwd=request.POST.get('pwd')
    cpwd=request.POST.get('cpwd')
    email=request.POST.get('email')
    allow=request.POST.get('allow')
    nums = UserInfo.objects.filter(uname=user_name).count()
    if nums>=1 :
        s = '用户名已存在！'
        return render(request,'ttsx/register.html',{'err':s})
    else:
        s1 = sha1()
        s1.update(pwd.encode())
        pwd_sha1 = s1.hexdigest()
        yhobj=UserInfo()
        yhobj.uname = user_name
        yhobj.upwd = pwd_sha1
        yhobj.umail = email
        yhobj.save()
        return redirect('/login/')




# def user_name(request):
#     user_name=request.GET.get('user_name')
#     nums=UserInfo.objects.filter(uname=user_name).count()
#     print(nums)
#     return JsonResponse({'nums':nums})