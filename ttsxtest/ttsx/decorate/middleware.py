#coding=utf-8
class UrlPathMiddleware:
    def process_request(self,request):
        # 如果当前请求的路径与用户登录、注册相关，则不需要记录
        if request.path not in ['/register/',
                                '/register_check/',
                                '/user_name/',
                                '/login/',
                                '/login_ajax_check/',
                                '/loginout/',
                                '/islogin/',
                                '/count/',
                                '/add/',
                                '/deletes/',
                                '/edit/',
                                '/place_order/',
                                '/cart/',
                                            ]:
            request.session['url_path'] = request.get_full_path()