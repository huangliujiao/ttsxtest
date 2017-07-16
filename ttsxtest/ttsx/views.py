#coding=utf-8
from django.shortcuts import render,redirect
from .models import *
from django.http import JsonResponse,response
from hashlib  import sha1
from .decorate import percolator
from django.core.paginator import Paginator
from django.db import transaction
import datetime
# Create your views here.
#登录页面
def login(request):
    #返回登录页面，title是页面标题,top是头部，base.html会根据这个值判断是否传给登录界面的头部,默认传入的值是top:1
    context = {'title': '登录', 'top': '0'}
    return render(request,'ttsx/login.html',context)
#注册页面
def register(request):
    #同上
    context = {'title': '注册', 'top': '0'}
    return render(request,'ttsx/register.html',context)
#退出函数
def loginout(request):
    #用户点击退出的时候会触发这个函数，然后删除session里面存储的用户信息
    del request.session['uid']
    # del request.session['uname']
    #重定向到登录页面
    return redirect('/login/')
#注册验证
def register_check(request):
    #用request.POST.get来获取到用户页面填写的信息
    user_name=request.POST.get('user_name')
    pwd=request.POST.get('pwd')
    cpwd=request.POST.get('cpwd')
    email=request.POST.get('email')
    allow = request.POST.get('allow')
    #根据页面get到的用户名获取数据库存储的所有信息并调用count方法统计该用户名有多少个
    nums = UserInfo.objects.filter(uname=user_name).count()
    #查找输入的邮箱值有没有@和.com
    email1=email.find('@')
    email2=email.find('.com')
    #判断输入的用户名、密码、勾选协议、邮箱
    if nums==0 and pwd==cpwd and allow =='on' and email1 != -1 and email2 != -1 :
        #根据引入的sha1包进行密码加密
        s1 = sha1()
        #对获取到的pwd密码要先进行转码
        s1.update(pwd.encode())
        #生成加密密码并赋值给pwd_sha1
        pwd_sha1 = s1.hexdigest()
        #获取到一个用户对象
        yhobj=UserInfo()
        #给用户对象的各个属性设置值
        yhobj.uname = user_name
        yhobj.upwd = pwd_sha1
        yhobj.umail = email
        #保存到数据库
        yhobj.save()
        #如果if之前的判断都相等则重定向到登录页面
        return redirect('/login/')
    else:
        #如果不相等，则返回到注册页面，并传入用户之前输入的用户名、密码、邮箱
        return render(request,'ttsx/register.html',{'user_name':user_name,'pwd':pwd,'email':email})
#判断用户是否登录
def islogin(request):
    result = 0
    if request.session.has_key('uid'):
        result = 1
        return JsonResponse({'islogin':result})
    else:
        return JsonResponse({'islogin':result})

#用户名验证是否被注册
def user_name(request):
    #获取到用户名
    user_name=request.POST.get('username')
    #获取到这个用户名在数据库里有多少个
    nums=UserInfo.objects.filter(uname=user_name).count()
    #JsonResponse返回数据库里有多少个用户名
    return JsonResponse({'nums':nums})

# ajax登录校验
def login_ajax_check(request):
    # 1.获取提交的用户名和密码
    uname = request.POST.get('uname')
    pwd = request.POST.get('pwd')
    #记住用户名
    ujz = request.POST.get('user_jz')
    #使用sha1加密
    s1 = sha1()
    s1.update(pwd.encode())
    pwd_sha1 = s1.hexdigest()
    #查询此用户名在数据库里存不存在
    yhobj = UserInfo.objects.filter(uname=uname)
    #存在则大于零
    if len(yhobj) > 0:
        #判断密码是否相等
        if yhobj[0].upwd == pwd_sha1 :
            #登录时获取到之前浏览的路径，设置在中间件里
            path=request.session.get('url_path')
            #使用Json返回
            response = JsonResponse({'res': 'ok','path':path})
            #记录登录用户id到session
            request.session['uid'] = yhobj[0].id
            #把用户名保存到cookie
            if(ujz=='true'):
                response.set_cookie('uname', uname, expires=datetime.datetime.now() + datetime.timedelta(days=14))
            else:
                response.set_cookie('uname', '', max_age=-1)
            return response
        else:
            return JsonResponse({'res':'perr'})
    else:
        return JsonResponse({'res': 'uerr'})

#用户中心
@percolator.perc
def user_center_info(request):
    #获取到当前用户对象
    user = UserInfo.objects.get(pk=request.session['uid'])
    #取数据库里最新的五个商品品
    recent_list=GoodsInfo.objects.all().order_by('-gclick')[0:5]
    #获取到存在cookie的商品id
    ids = request.COOKIES.get('goods_ids').split(',')[:-1]
    #根据id获取到所有cookie里面的商品
    goods_ids=GoodsInfo.objects.filter(id__in=ids)
    context = {'user': user,'recent_list':recent_list,'goods_ids':goods_ids}
    return render(request,'ttsx/user_center_info.html',context)

#我的订单
@percolator.perc
def user_center_order(request):
    user = UserInfo.objects.get(pk=request.session['uid'])
    order_list = OrderMain.objects.filter(user_id=request.session.get('uid'))
    paginator = Paginator(order_list, 3)
    pindex = int(request.GET.get('pindex', '1'))
    page = paginator.page(pindex)
    page_list = []
    if paginator.num_pages < 5:
        page_list = paginator.page_range
    elif pindex <= 2:
        page_list = range(1, 6)
    elif pindex >= paginator.num_pages - 1:  # 6 7 8   9 10
        page_list = range(paginator.num_pages - 4, paginator.num_pages + 1)
    else:
        page_list = range(pindex - 2, pindex + 3)

    context = {'user': user,'title': '用户订单', 'order_page': page, 'page_list': page_list}
    return render(request,'ttsx/user_center_order.html',context)

#我的收货地址
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

#首页
def index(request):
    #获取到所有商品类型
    type_list = TypeInfo.objects.all()
    #建立空数组
    list1 = []
    #循环商品类型
    for type1 in type_list:
        #根据当前商品类型对象，倒序取到当前类型里的所有商品里的前四个商品对象
        new_list = type1.goodsinfo_set.order_by('-id')[0:4]
        # 根据当前商品类型对象，倒序取到当前类型里的所有商品里的前四个商品点击量
        click_list = type1.goodsinfo_set.order_by('-gclick')[0:4]
        #每次循环当前商品类型对象就把上面得到的值存入新数组
        list1.append({'new_list': new_list, 'click_list': click_list, 't1': type1})
    #判断是否登录
    if request.session.has_key('uid'):
        #根据之前储存的session['uid']获取到当前用户
        user = UserInfo.objects.get(pk=request.session['uid'])
        #把要传给页面的参数放到数组中，user当前对象,nav在base页面判断传入1则显示用户搜索框、list1是上面循环查询到的值
        context = {'user': user,'title': '首页', 'nav': '0','list1':list1}
        return render(request,'ttsx/index.html',context)
    else:
        #同上
        context = {'list1': list1, 'title': '首页', 'nav': '0'}
        return render(request,'ttsx/index.html',context)

#商品信息
def detail(request,id):
    #获取到跳转路径的值
    nums = request.get_full_path().split('/')[1]
    #根据值进行查找并返回该商品对象
    gs = GoodsInfo.objects.get(pk=nums)
    # 保存商品浏览量
    gs.gclick = gs.gclick +1
    gs.save()
    #根据商品一对多关联的ID查找到Typeinfo的相关信息
    type1 = TypeInfo.objects.get(id=gs.gtype_id)
    #根据type1商品类型的ID获取到数据库最后两个商品信息
    new_list = GoodsInfo.objects.filter(gtype_id=type1.id).order_by('-id')[0:2]
    #如果该用户登录了就执行if
    if request.session.has_key('uid'):

        #获取到用户对象传入页面，base页面会判断是否传入用户信息
        user = UserInfo.objects.get(pk=request.session['uid'])
        #user用户对象、title网页名称、nav在base页面判断传入1则显示用户搜索框、gs是当前商品对象、t1是商品类型对象、new_list是最后两个商品信息
        context = {'user': user,'title': '商品信息', 'nav': '0','gs':gs,'t1':type1,'new_list':new_list}
        response = render(request, 'ttsx/detail.html',context)
        #获取到所有cookie里的商品id
        ids = request.COOKIES.get('goods_ids', '').split(',')
        #判断是否有是不是五个
        if id in ids:
            ids.remove(id)
        ids.insert(0, id)
        if len(ids) > 6:
            ids.pop()
        #保存点击的商品到cookie里的ids
        response.set_cookie('goods_ids', ','.join(ids), max_age=60 * 60 * 24 * 7)
        return response
    else:
        context = {'title': '商品信息','gs':gs, 'nav': '0','t1':type1,'new_list':new_list}
        return render(request,'ttsx/detail.html',context)
#列表商品
def list(request,tid, pindex):
    # ym = request.get_full_path().split('/')
    #根据页面传入的pid参数获取到当前商品类型对象
    type1 = TypeInfo.objects.get(id=int(tid))
    #根据pid获取到所有商品对象，-id代表获取到的数据为倒序
    gs_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-id')
    #根据上面的操作获取到数据库最后两个商品的对象
    new_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-id')[0:2]
    #引用Paginator类对获取到的商品对象分页显示，每页五个
    p = Paginator(gs_list,5)
    #根据传入的pindex获取到当前的页码
    page=p.page(int(pindex))
    #判断是否登录
    if request.session.has_key('uid'):
        #获取到当前用户
        user = UserInfo.objects.get(pk=request.session['uid'])
        #user当前用户、title当前页面标题、nav根据base判断传入的搜索框部分。t1是商品类型对象、page当前页码、new_list最后两个商品对象
        context = {'user': user, 'title': '商品列表', 'nav': '0','t1':type1,
                   'page':page,'new_list':new_list,'mr':'active'}

        return render(request,'ttsx/list.html',context)
    else:
        #同上
        context = {'title': '商品列表', 'nav': '0', 't1': type1,
                   'page': page, 'new_list': new_list, 'mr': 'active'}
        return render(request,'ttsx/list.html',context)
#按价格排序列表
def list_price(request,tid,pindex):
    ym = request.get_full_path().split('/')
    # 根据页面传入的pid参数获取到当前商品类型对象
    type1 = TypeInfo.objects.get(id=int(tid))
    if ym[4]=='?sort':
        # 根据pid获取到所有商品对象，-id代表获取到的数据为倒序
        gs_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-gprice')
        sort = 1
    else:
        gs_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('gprice')
        sort = 0
    # 根据上面的操作获取到数据库最后两个商品的对象
    new_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-id')[0:2]
    # 引用Paginator类对获取到的商品对象分页显示，每页五个
    p = Paginator(gs_list, 5)
    # 根据传入的pindex获取到当前的页码
    page = p.page(int(pindex))
    # 判断是否登录
    if request.session.has_key('uid'):
        # 获取到当前用户
        user = UserInfo.objects.get(pk=request.session['uid'])
        # user当前用户、title当前页面标题、nav根据base判断传入的搜索框部分。t1是商品类型对象、page当前页码、new_list最后两个商品对象
        context = {'user': user, 'title': '商品列表', 'nav': '0','sort':sort, 't1': type1, 'page': page, 'new_list': new_list,'jg':'active'}
        return render(request, 'ttsx/list.html', context)
    else:
        # 同上
        context = {'title': '商品列表', 'nav': '0', 'sort': sort, 't1': type1, 'page': page,
                   'new_list': new_list, 'jg': 'active'}
        return render(request, 'ttsx/list.html', context)
#按点击量排序列表
def list_click(request,tid,pindex):
    ym = request.get_full_path().split('/')
    # 根据页面传入的pid参数获取到当前商品类型对象
    type1 = TypeInfo.objects.get(id=int(tid))
    # 根据pid获取到所有商品对象，-id代表获取到的数据为倒序
    if ym[4]=='?sort':
        # 根据pid获取到所有商品对象，-id代表获取到的数据为倒序
        gs_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-gclick')
        sort = 1
    else:
        gs_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('gclick')
        sort = 0
    # 根据上面的操作获取到数据库最后两个商品的对象
    new_list = GoodsInfo.objects.filter(gtype_id=int(tid)).order_by('-id')[0:2]
    # 引用Paginator类对获取到的商品对象分页显示，每页五个
    p = Paginator(gs_list, 5)
    # 根据传入的pindex获取到当前的页码
    page = p.page(int(pindex))
    # 判断是否登录
    if request.session.has_key('uid'):
        # 获取到当前用户
        user = UserInfo.objects.get(pk=request.session['uid'])
        # user当前用户、title当前页面标题、nav根据base判断传入的搜索框部分。t1是商品类型对象、page当前页码、new_list最后两个商品对象
        context = {'user': user, 'title': '商品列表', 'nav': '0', 't1': type1, 'page': page,
                   'new_list': new_list,'rq':'active','sort':sort}
        return render(request, 'ttsx/list.html', context)
    else:
        # 同上
        context = { 'title': '商品列表', 'nav': '0', 't1': type1, 'page': page,
                   'new_list': new_list, 'rq': 'active', 'sort': sort}
        return render(request, 'ttsx/list.html', context)
#购物车
def cart(request):
    try:
        #判断当前用户是否登录
        if request.session.has_key('uid'):
            #获取到当前用户
            user = UserInfo.objects.get(pk=request.session['uid'])
            #获取到当前用户的所有商品
            cart_list = CartInfo.objects.filter(user_id=user.id)
            context = {'user': user, 'title': '购物车', 'nav': '0','cart_list':cart_list}
            return render(request,'ttsx/cart.html',context)
        else:
            context = {'title': '购物车'}
            return render(request, 'ttsx/login.html',context)
    except:
        return render(request,'ttsx/404.html')
#商品支付
def place_order(request):
    try:
        #getlist获取到所有返回的cartGoods参数
        cartGoods=request.GET.getlist('cartGoods')
        #根据返回的id获取到所有商品对象
        cart_list = CartInfo.objects.filter(id__in=cartGoods)
        user = UserInfo.objects.get(pk=request.session['uid'])
        return render(request,'ttsx/place_order.html',{'user':user,'cart_list':cart_list, 'cart_ids': ','.join(cartGoods)})
    except:
        return render(request, 'ttsx/404.html')

#添加
def add(request):
    try:
        #获取到用户id和商品id
        uid=request.session.get('uid')
        gid=int(request.GET.get('gid'))
        #获取传来的商品参数，默认商品数量为1
        count = int(request.GET.get('count','1'))
        #查询该用户购买的商品数量
        counts=CartInfo.objects.filter(goods_id=gid,user_id=uid).count()
        #如果有商品，则get到该商品，并给其商品数量+count个
        if counts>0:
            usergs = CartInfo.objects.get(goods_id=gid,user_id=uid)
            usergs.count +=count
            usergs.save()
            return JsonResponse({'isadd': 1})
        #没有商品则创建该商品，并保存
        else:
            cart=CartInfo()
            cart.user_id = uid
            cart.goods_id = gid
            cart.count = count
            cart.save()
            return JsonResponse({'isadd':1})
    except:
        return JsonResponse({'isadd':0})
#删除
def deletes(request):
    try:
        #get到传来的cid并从该表中删除
        cid=request.GET.get('cid')
        cgoos=CartInfo.objects.get(id=cid)
        cgoos.delete()
        return JsonResponse({'msg':'ok'})
    except:
        return JsonResponse({'msg':'err'})
#统计
def count(request):
    # 判断当前用户是否登录
    if request.session.has_key('uid'):
        # 获取到当前用户
        userCounts = CartInfo.objects.filter(user_id=request.session['uid'])
        count = 0
        #统计该用户添加到购物车的所有商品
        for user in userCounts:
            count += user.count
        return JsonResponse({'count':count})
#修改
def edit(request):
    #获取页面传来需要修改的cid和数量
    cid=request.GET.get('cid')
    numShow = request.GET.get('numShow')
    #会根据cid得到对象并对数据进行修改
    cartobj=CartInfo.objects.get(id=cid)
    cartobj.count = numShow
    cartobj.save()
    return JsonResponse({'count':numShow})

#全文检索
def search_action(request):
    #获取到查询的关键字
    commodity = request.GET.get('commodity')
    #判断如果get到页码就跳到相应的页面，否则就跳到第一页
    if request.GET.get('page'):
        pindex=request.GET.get('page')
        pindex=int(pindex)
    else:
        pindex = 1
    #查找包含此关键字的所有商品
    gs_list = GoodsInfo.objects.filter(gtitle__contains=commodity)
    # 引用Paginator类对获取到的商品对象分页显示，每页五个
    p = Paginator(gs_list, 6)
    # 根据获取的pindex获取到当前的页码
    page_list=p.page_range
    page_obj = p.page(pindex)
    #判断是否登录
    if request.session.has_key('uid'):
        user = UserInfo.objects.get(pk=request.session['uid'])
        context = {'page_obj':page_obj,'commodity':commodity,'nav':'0','page_list':page_list,'user': user, 'title': '搜素页'}
    else:
        context = {'page_obj': page_obj, 'commodity': commodity,'nav':'0', 'page_list': page_list}
    return render(request,'search/search.html',context)

@transaction.atomic
def do_order(request):
    sid=transaction.savepoint()
    is_commit = True
    try:
        #获取请求的购物车信息
        cart_ids=request.POST.get('c_ids').split(',')
        #创建订单主表
        main=OrderMain()
        time_str=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        user_id=request.session.get('uid')
        main.orderid='%s%d'%(time_str,user_id)
        main.user_id=user_id
        main.save()
        #逐个遍历购物车中的商品，进行数量与库存的判断，，
        cart_list=CartInfo.objects.filter(id__in=cart_ids)
        total=0
        for cart in cart_list:
            if cart.count<=cart.goods.gkucun:
                #如果库存足够则添加到详单
                detail=OrderDetail()
                detail.order=main
                detail.goods=cart.goods
                detail.count=cart.count
                detail.price=cart.goods.gprice
                total+=cart.count*cart.goods.gprice
                detail.save()
                #修改库存
                cart.goods.gkucun-=cart.count
                cart.goods.save()
                #删除购物车
                cart.delete()
            else:
                #如果库存不够则购买失败回滚
                transaction.savepoint_rollback(sid)
                is_commit=False
                break
        if is_commit:
            main.total=total
            main.save()
            transaction.savepoint_commit(sid)
    except:
        is_commit=False
        transaction.savepoint_rollback(sid)
    # 返回response对象
    if is_commit:
        return redirect('/user_center_order/')
    else:
        return redirect('/cart/')

