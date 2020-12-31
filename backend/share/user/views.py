import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
import django.contrib.auth as auth
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import QueryDict

from user.models import Verification, User
import hashlib
import base64
from datetime import datetime, timezone, timedelta

# 加密

import time
CODE = {
    "success": 200,
    "database_error": 300,
    "user_error": 400,
    "method_error": 600,
    "parameter_error": 700,
}

gen_response = {
    'success': {
        "code": 200,
        "data": {
            "msg": "success"
        }
    },
    'method_err': {
        "code": 600,
        "data": {
            "msg": "wrong method"
        }
    },
    'param_err': {
        "code": 700,
        "data": {
            "msg": "wrong parameter"
        }
    },
    'post_not_exist': {
        "code": 300,
        "data": {
            "msg": "post not exists"
        }
    },
    'user_not_exist': {
        "code": 300,
        "data": {
            "msg": "user not exists"
        }
    },
    'user_error': {
        "code": 400,
        "data": {
            "msg": "not authorized"
        }
    }
}

@csrf_exempt
def change_password(request):
    code = -1
    msg = ''
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse(gen_response["user_error"])
        

        data = json.loads(request.body)
        user = User.objects.get(id = request.user.id)
        old_password = data.get('oldpass')
        new_1_password = data.get('newpass')

        new_avatar = data.get('newAvatarUrl')
        new_username = data.get('newUserName')

        msg = 'change correct'
        response = {
            'code': 200,
            'data': {
                'msg': msg
            }
        }
        
        if new_avatar:
            user.avatar = new_avatar
            user.save()
            return JsonResponse(response)

        if new_username:
            user.username = new_username
            user.save()
            return JsonResponse(response)
        
        if not user.sha256_password == old_password:
            return JsonResponse(gen_response['param_err'])
        
        user.sha256_password = new_1_password
        user.save()
        return JsonResponse(response)

    else:
        code = CODE['method_error']
        msg = 'wrong method'

    response = {
        'code': code,
        'data': {
            'msg':msg,
        }
    }
    return JsonResponse(response)

@csrf_exempt
def check_login(request):
    code = -1
    msg = ''
    mystr = request.CHECK.get('mystr')
    mystr =  base64.b64decode(mystr).decode("utf-8")
    mylist = mystr.split(' ', 1)
    username = mylist[0]
    time = mylist[1]
    now = timezone.now()
    if now > time + 120 :
        msg = 'long time error'
    else:
        msg = 'ok'

    response = {
        'code': 400,
        'data': {
            'msg': msg
        }
    }
    return JsonResponse(response)

@csrf_exempt
def register_validation(request):
    code = -1
    msg = ''
    user_profile = {}
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        username = data.get('userName')
        password = data.get('passwordHash')
        verification_code = data.get('verificationCode')

        if email is None or username is None or password is None or verification_code is None:
            code = CODE['parameter_error']
            msg = 'wrong parameter'

        else:
            email += "@pku.edu.cn"
            try:
                validate_email(email)
                if User.objects.filter(pku_mail=email).exists():
                    code = CODE['database_error']
                    msg = 'email already registered'
                elif str(verification_code) \
                        != Verification.objects.get(pku_mail=email).verification_code:
                    code = CODE['parameter_error']
                    msg = 'wrong verification code'
                elif User.objects.filter(username=username).exists():
                    code = CODE['database_error']
                    msg = "duplicate username"
                else:
                    user = User.objects.create_user(username=username, password=password,
                                            pku_mail=email)
                    user.sha256_password = password
                    user.save()

                    auth.login(request, user)
                    user = User.objects.get(id=user.id)
                    user_profile['user'] = {'name':user.username, "userID":user.id}
                    user_profile['email'] = user.pku_mail
                    user_profile['is_admin'] = user.is_superuser
                    code = CODE['success']
                    msg = 'success'
            except ValidationError:
                code = CODE['parameter_error']
                msg = 'wrong email'
    else:
        code = CODE['method_error']
        msg = 'wrong method'

    response = {
        'code': code,
        'data': {
            'msg':msg,
            "profile": user_profile,
        }
    }
    return JsonResponse(response)

@csrf_exempt
def register(request):
    code = -1
    msg = ''
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        if email is None:
            code = CODE['parameter_error']
            msg = 'wrong email'
        else:
            email += "@pku.edu.cn"

            try:
                validate_email(email)

                if User.objects.filter(pku_mail=email).exists():
                    code = CODE['database_error']
                    msg = 'email already registered'

                else:
                    result = Verification.get_verification_code(email)
                    if result[0] == -1:
                        code = CODE['user_error']
                        msg = 'repeated acquisition in 30 seconds'

                    else:
                        send_mail('资料分享平台', str(result[1]), '980166150@qq.com', [email])
                        code = CODE['success']
                        msg = 'success'

            except ValidationError:
                code = CODE['parameter_error']
                msg = 'wrong email'

    else:
        code = CODE['method_error']
        msg = 'wrong method'
    response = {
        'code': code,
        'data': {
            'msg':msg
        }
    }
    return JsonResponse(response)

@csrf_exempt
def login(request):
    code = -1
    msg = ''
    user_profile = {}
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = "lf20010218"#data.get('password')
        if email is None or password is None:
            code = CODE['parameter_error']
            msg = 'wrong parameter'
        else:
            email += "@pku.edu.cn"
            if not User.objects.filter(pku_mail=email).exists():
                code = CODE['parameter_error']
                msg = 'email or password error'


            else:
                username = User.objects.get(pku_mail=email).username
                user = User.objects.get(pku_mail=email)
                if user.sha256_password != password:
                    user = None

                # user = auth.authenticate(username=username, password=password)
                if user is None:
                    code = CODE['parameter_error']
                    msg = 'email or password error'

                else:
                    auth.login(request, user)
                    user = User.objects.get(id=user.id)
                    user_profile['user'] = {'name':user.username, "userID":user.id}
                    user_profile['email'] = user.pku_mail
                    user_profile['is_admin'] = user.is_superuser
                    code = CODE['success']
                    msg = 'success'

    else:
        code = CODE['method_error']
        msg = 'wrong method'
    '''
    now = timezone.now()
    #sha256_username = hashlib.sha256(bytes(username, encoding="utf-8")).hexdigest()
    sha256_username = base64.b64encode(username.encode('utf-8')).decode('ascii')
    #sha256_now = hashlib.sha256(bytes(now, encoding="utf-8")).hexdigest()
    sha256_now = base64.b64encode(now.encode('utf-8')).decode('ascii')
    sha_256_char = sha256_username + ' ' + sha256_now
    '''
    response = {
        'code': code,
        'data': {
            'msg':msg,
#            'token':sha_256_char,
            "profile": user_profile,
        }
    }
    return JsonResponse(response)

@csrf_exempt
def password(request):
    code = -1
    msg = ''
    user_profile = {}
    if request.method == 'GET':
        email = request.GET.get('email')
        if email is None:
            code = CODE['parameter_error']
            msg = 'wrong parameter'
        else:
            email += "@pku.edu.cn"
            try:
                validate_email(email)
                user = User.objects.filter(pku_mail=email)
                if user.exists():
                    user = user[0]
                    result = Verification.get_verification_code(user.pku_mail, "password")
                    if result[0] == -1:
                        code = CODE['user_error']
                        msg = 'repeated acquisition in 30 seconds'
                    else:
                        send_mail('修改密码验证码', str(result[1]), '980166150@qq.com', [email])
                        code = CODE['success']
                        msg = 'success'
                else:
                    code = CODE['parameter_error']
                    msg = 'wrong email'
            except ValidationError:
                code = CODE['parameter_error']
                msg = 'wrong email'
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        verification_code = request.POST.get('verificationCode')
        if email is None or password is None or verification_code is None:
            code = CODE['parameter_error']
            msg = 'wrong parameter'
        else:
            email += "@pku.edu.cn"
            try:
                validate_email(email)
                veri = Verification.objects.filter(pku_mail=email)
                if veri.exists() and veri[0].verification_code == str(verification_code):
                    user = User.objects.get(pku_mail=email)
                    user.set_password(password)
                    user.sha256_password = password
                    user.save()
                    code = CODE['success']
                    msg = 'success'
                else:
                    code = CODE['parameter_error']
                    msg = 'wrong verification code'
            except ValidationError:
                code = CODE['parameter_error']
                msg = 'wrong email'
    else:
        code = CODE['method_error']
        msg = 'wrong method'

    response = {
        'code': code,
        'data': {
            'msg':msg,
        }
    }
    return JsonResponse(response)

@csrf_exempt
def logout(request):
    code = -1
    msg = ''
    if request.method == 'POST':
        auth.logout(request)
        code = CODE['success']
        msg = 'success'
    else:
        code = CODE['method_error']
        msg = 'wrong method'
    response = {
        'code': code,
        'data': {
            'msg':msg
        }
    }
    return JsonResponse(response)

@csrf_exempt
def profile(request):
    code = -1
    msg = ''
    user_profile = {}
    if not request.user.is_authenticated:
        code = CODE['user_error']
        msg = "not authorized"
    else:
        if request.method == 'GET':
            user_id = request.GET.get("userID") if request.GET.get("userID") else request.user.id
            if User.objects.filter(id=user_id).exists():
                user = User.objects.get(id=user_id)
                user_profile['user'] = {'name':user.username, "userID":user.id}
                user_profile['email'] = user.pku_mail
                user_profile['is_admin'] = user.is_superuser
                code = CODE['success']
                msg = 'success'
            else:
                code = CODE['database_error']
                msg = 'user does not exist'
        else:
            code = CODE['method_error']
            msg = 'wrong method' + request.method
    response = {
        'code': code,
        'data': {
            'msg': msg,
            'profile': user_profile,
        }
    }
    return JsonResponse(response)
