#coding=utf-8
from django.shortcuts import redirect
def perc(func):
    def inner(request,*args,**kwargs):
        if request.session.has_key('uid'):
            return func(request,*args,**kwargs)
        else:
            return redirect('/login/')
    return inner