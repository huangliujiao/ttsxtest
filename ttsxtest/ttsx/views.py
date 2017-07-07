#coding=utf-8
from django.shortcuts import render,redirect
from .models import *
from django.http import JsonResponse,HttpResponse
from hashlib  import sha1
from .decorate import percolator
import datetime

# Create your views here.

def login(request):
    context = {'title': '登录', 'top': '0'}
    return render(request,'ttsx/login.html',context)
def register(request):
    context = {'title': '注册', 'top': '0'}
    return render(request,'ttsx/register.html',context)
def loginout(request):
    del request.session['uid']
    # del request.session['uname']
    return redirect('/login/')

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
    if len(yhobj) > 0:
        if yhobj[0].upwd == pwd_sha1 :
            path=request.session.get('url_path')

            # path=str(path)
            print(path)
            response = JsonResponse({'res': 'ok','path':path})
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

@percolator.perc
def user_center_info(request):
    user = UserInfo.objects.get(pk=request.session['uid'])
    context = {'user': user}
    return render(request,'ttsx/user_center_info.html',context)

@percolator.perc
def user_center_order(request):
    user = UserInfo.objects.get(pk=request.session['uid'])
    context = {'user': user}
    return render(request,'ttsx/user_center_order.html',context)

@percolator.perc
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

def index(request):
    type_list = TypeInfo.objects.all()
    list1 = []
    for type1 in type_list:
        new_list = type1.goodsinfo_set.order_by('-id')[0:4]
        click_list = type1.goodsinfo_set.order_by('-gclick')[0:4]
        list1.append({'new_list': new_list, 'click_list': click_list, 't1': type1})

    if request.session.has_key('uid'):
        user = UserInfo.objects.get(pk=request.session['uid'])
        context = {'user': user,'title': '首页', 'nav': '0','list1':list1}
        return render(request,'ttsx/index.html',context)
    else:
        context = {'list1': list1, 'title': '首页'}
        return render(request,'ttsx/index.html',context)

def detail(request):
    s = request.get_full_path()
    nums = s.split('/')[1]
    print(nums)
    gs=GoodsInfo.objects.get(id=nums)
    if request.session.has_key('uid'):
        user = UserInfo.objects.get(pk=request.session['uid'])
        context = {'user': user,'title': '商品信息', 'nav': '0','gs':gs}
        return render(request, 'ttsx/detail.html',context)
    else:
        context = {'title': '商品信息','gs':gs}
        return render(request,'ttsx/detail.html',context)

def cart(request):
    if request.session.has_key('uid'):
        user = UserInfo.objects.get(pk=request.session['uid'])
        context = {'user': user, 'title': '购物车', 'nav': '0'}
        return render(request,'ttsx/cart.html',context)
    else:
        context = {'title': '购物车'}
        return render(request, 'ttsx/cart.html',context)



