#coding=utf-8
from django.conf.urls import url
from . import views
from .search_view import *
urlpatterns = [
    url(r'^login/$',views.login),
    url(r'^register/$',views.register),
    url(r'^register_check/$',views.register_check),
    url(r'^user_name/$',views.user_name),
    url(r'^login_ajax_check/$',views.login_ajax_check),
    url(r'^user_center_info/$',views.user_center_info),
    url(r'^user_center_order/$',views.user_center_order),
    url(r'^user_center_site/$',views.user_center_site),
    url(r'^list/(\d+)/(\d+)/$',views.list),
    url(r'^list_price/(\d+)/(\d+)/$',views.list_price),
    url(r'^list_click/(\d+)/(\d+)/$',views.list_click),
    url(r'^$',views.index),
    url(r'^loginout/$',views.loginout),
    url('^search_action/$', views.search_action),
    url(r'^(\d+)/$',views.detail),
    url(r'^islogin/$',views.islogin),
    url(r'^cart/$', views.cart),
    url(r'^add/$', views.add),
    url(r'^count/$', views.count),
    url(r'^place_order/$',views.place_order),
    url(r'^edit/$',views.edit),
    url(r'^deletes/$',views.deletes),
    url(r'^do_order/$',views.do_order),

]