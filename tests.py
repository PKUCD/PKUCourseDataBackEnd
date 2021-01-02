# -*- coding: utf-8 -*-
from django.test import TestCase
from django.http import HttpResponse, JsonResponse
from .models import Verification, User
import django.contrib.auth as auth
import time

from demo.config import CODE
import hashlib

def hash(passwrod):
    return hashlib.sha256(bytes(passwrod, encoding="utf-8")).hexdigest()

class UserTests(TestCase):
    def test_regiser(self):
        u = User.objects.create_user(username='pkucd', password='123456', pku_mail='pkucathelper@pku.edu.cn')
        u.sha256_password = hash("123456")
        u.save()

        # 方法错误
        response = self.client.get('/user/register')
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['method_error'])

        response = self.client.put('/user/register')
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['method_error'])

        response = self.client.delete('/user/register')
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['method_error'])

        # 邮箱格式错误
        response = self.client.post('/user/register')
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['parameter_error'])

        response = self.client.post('/user/register', {'email': "pkucd@pku.edu.cn"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['parameter_error'])

        # 邮箱已注册
        response = self.client.post('/user/register', {'email': "pkucathelper"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['database_error'])

        # 成功
        response = self.client.post('/user/register', {'email': "pkucd"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['success'])

        # 成功
        response = self.client.post('/user/register', {'email': "180001281"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['success'])

        # 30s内重复请求
        response = self.client.post('/user/register', {'email': "pkucd"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['user_error'])

        verification_code = Verification.objects.get(pku_mail='pkucd@pku.edu.cn').verification_code

        # 参数错误-无用户名
        response = self.client.post('/user/register_validation',
            {'password':'123456', 'email': "pkucd",
             'verificationCode':verification_code})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['parameter_error'])

        # 参数错误-无密码
        response = self.client.post('/user/register_validation',
            {'username':'pkucd', 'email': "pkucd",
             'verificationCode':verification_code})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['parameter_error'])

        # 参数错误-无邮箱
        response = self.client.post('/user/register_validation',
            {'username':'pkucd', 'password':'123456',
             'verificationCode':verification_code})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['parameter_error'])

        # 参数错误-无验证码
        response = self.client.post('/user/register_validation',
            {'username':'pkucd', 'password':'123456', 'email': "pkucd"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['parameter_error'])

        # 参数错误-验证码错误
        wrong_code = int(verification_code)-1 if int(verification_code)>500000 else int(verification_code)+1
        response = self.client.post('/user/register_validation',
            {'username':'pkucd', 'password':'123456', 'email': "pkucd",
             'verificationCode':wrong_code})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['parameter_error'])

        # 用户名重复
        response = self.client.post('/user/register_validation',
            {'username':'pkucathelper', 'password':'123456', 'email': "pkucd",
             'verificationCode':verification_code})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['database_error'])

        # 邮箱格式错误
        response = self.client.post('/user/register_validation',
            {'username':'pkucd', 'password':'123456', 'email': "pkucd@pku.edu.cn",
             'verificationCode':verification_code})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['parameter_error'])

        # 成功
        response = self.client.post('/user/register_validation',
            {'username':'pkucd', 'password':'123456', 'email': "pkucd",
             'verificationCode':verification_code})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['success'])

        verification_code = Verification.objects.get(pku_mail='180001281@pku.edu.cn').verification_code

        # 用户名已存在
        response = self.client.post('/user/register_validation',
            {'username':'pkucd', 'password':'123456', 'email': "180001281",
             'verificationCode':verification_code})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['database_error'])

    def test_login(self):
        u = User.objects.create_user(username='pkucd', password='123456', pku_mail='pkucd@pku.edu.cn')
        u.sha256_password = hash("123456")
        u.save()
        u = User.objects.create_user(username='cd', password='123456', pku_mail='180001281@pku.edu.cn')
        u.sha256_password = hash("123456")
        u.save()

        # 方法错误
        response = self.client.get('/user/login')
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['method_error'])

        response = self.client.put('/user/login')
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['method_error'])

        response = self.client.delete('/user/login')
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['method_error'])

        # 参数错误
        response = self.client.post('/user/login', {'password':'123456'})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['parameter_error'])

        response = self.client.post('/user/login', {'username':'pkucd'})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['parameter_error'])

        # 账户或密码错误
        response = self.client.post('/user/login', {'username':'pkucd', 'password':'1234567'})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['parameter_error'])

        # 成功
        response = self.client.post('/user/login', {'email':'pkucd', 'password':hash('123456')})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['success'])

        # 重复请求登录
        response = self.client.post('/user/login', {'email':'pkucd', 'password':hash('123456')})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['success'])

        # 请求另外一个账户登录
        response = self.client.post('/user/login', {'email':'1800012811', 'password':hash('123456')})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['user_error'])

    def test_change_password(self):
        # 账户错误
        response = self.client.post('/user/change_password', {'username': 'pkucd', 'password': '1234567'})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['user_error'])

        # 密码错误
        response = self.client.post('/user/change_password', {'username': 'pkucd', 'password': '1234567'})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['old_code_error'])

        # 新密码与确认密码不同
        response = self.client.post('/user/change_password', {'username': 'pkucd', 'password': '1234567'})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['different_code_error'])

        # token无法解密
        response = self.client.post('/user/change_password', {'username': 'pkucd', 'password': '1234567'})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['token_error'])

        # 成功
        response = self.client.post('/user/change_password', {'username': 'pkucd', 'password': '1234567'})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['success'])

    def test_password(self):
        u = User.objects.create_user(username='pkucd', password='123456', pku_mail='pkucd@pku.edu.cn')
        u.sha256_password = hash("123456")
        u.save()

        response = self.client.get('/user/password', {"email":"pkucd"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], CODE['success'])
        pass
