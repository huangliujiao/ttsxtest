#coding=utf-8
from django.shortcuts import render,redirect
from .models import UserInfo
from django.http import JsonResponse,HttpResponse
from hashlib  import sha1
import datetime

# Create your views here.
def index(request):
    return render(request,'ttsx/index.html')
def login(request):
    return render(request,'ttsx/login.html')
def register(request):
    return render(request,'ttsx/register.html')


def register_check(request):
    user_name=request.POST.get('user_name')
    pwd=request.POST.get('pwd')
    cpwd=request.POST.get('cpwd')
    email=request.POST.get('email')
    allow = request.POST.get('allow')
    nums = UserInfo.objects.filter(uname=user_name).count()
    email1=email.find('@')
    email2=email.find('.com')
    print(email1)
    print(email2)
    if nums==0 and pwd==cpwd and allow =='on' and email1 != -1 and email2 != -1 :
        s1 = sha1()
        s1.update(pwd.encode())
        pwd_sha1 = s1.hexdigest()
        yhobj=UserInfo()
        yhobj.uname = user_name
        yhobj.upwd = pwd_sha1
        yhobj.umail = email
        yhobj.save()
        return redirect('/login/')
    else:
        return render(request,'ttsx/register.html',{'user_name':user_name,'pwd':pwd,'email':email})

def user_name(request):
    user_name=request.POST.get('username')
    nums=UserInfo.objects.filter(uname=user_name).count()
    return JsonResponse({'nums':nums})


# ajax登录校验
def login_ajax_check(request):
    # 1.获取提交的用户名和密码
    uname = request.POST.get('uname')
    pwd = request.POST.get('pwd')
    ujz = request.POST.get('user_jz')
    s1 = sha1()
    s1.update(pwd.encode())
    pwd_sha1 = s1.hexdigest()
    yhobj = UserInfo.objects.filter(uname=uname)
    print(len(yhobj))
    print(ujz)
    print(uname)
    print(pwd)
    if len(yhobj) > 0:
        if yhobj[0].upwd == pwd_sha1 :
            # response = redirect('/user/',{'res':'ok'})
            response = JsonResponse({'res': 'ok'})
            request.session['uid'] = yhobj[0].id

            if(ujz=='true'):
                response.set_cookie('uname', uname, expires=datetime.datetime.now() + datetime.timedelta(days=14))
            else:
                response.set_cookie('uname', '', max_age=-1)
            return response
        else:
            return JsonResponse({'res':'perr'})
    else:
        return JsonResponse({'res': 'uerr'})
def user_center_info(request):
    user = UserInfo.objects.get(pk=request.session['uid'])
    context = {'user': user}
    return render(request,'ttsx/user_center_info.html',context)

def user_center_order(request):
    user = UserInfo.objects.get(pk=request.session['uid'])
    context = {'user': user}
    return render(request,'ttsx/user_center_order.html',context)

def user_center_site(request):
    user = UserInfo.objects.get(pk=request.session['uid'])
    if request.method == 'POST':
        adrse=request.POST.get('addressee')
        adrs = request.POST.get('address')
        code = request.POST.get('code')
        phone = request.POST.get('phone')

        user.ushou = adrse
        user.uaddress = adrs
        user.ucode = code
        user.uphone= phone
        user.save()
    context = {'user': user}
    return render(request,'ttsx/user_center_site.html',context)


def cart(request):
    return render(request,'ttsx/cart.html')



