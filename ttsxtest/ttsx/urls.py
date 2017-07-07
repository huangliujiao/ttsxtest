#coding=utf-8
from django.conf.urls import url
from . import views
urlpatterns = [
    url(r'^login/$',views.login),
    url(r'^register/$',views.register),
    url(r'^register_check/$',views.register_check),
    url(r'^user_name/$',views.user_name),
    url(r'^login_ajax_check/$',views.login_ajax_check),
    url(r'^user_center_info/$',views.user_center_info),
    url(r'^user_center_order/$',views.user_center_order),
    url(r'^user_center_site/$',views.user_center_site),
    url(r'^cart/$',views.cart),
    url(r'^index/$',views.index),
    url(r'^loginout/$',views.loginout),
]