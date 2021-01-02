# -*- coding: utf-8 -*-
from django.test import TestCase
from django.http import HttpResponse, JsonResponse
from .models import Verification, User
import django.contrib.auth as auth
import time


class UserTests(TestCase):
    def test_regiser(self):
        u = User.objects.create_user(username='test', password='123456', pku_mail='1800013044')
        u.sha256_password = "123456"
        u.save()

        #邮箱已经注册
        response = self.client.post('/user/register', {'email': "1800013105"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 700)

        # 成功
        response = self.client.post('/user/register', {'email': "1800013044"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

        # 重复请求
        response = self.client.post('/user/register', {'email': "1800013044"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 400)

        verification_code = Verification.objects.get(pku_mail='1800013044@pku.edu.cn').verification_code

        # 成功
        response = self.client.post('/user/register_validation',
                                    {'username':'test', 'password':'123456', 'email': "1800013044",
                                     'verificationCode':verification_code})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

    def test_login(self):
        u = User.objects.create_user(username='test1', password='123456', pku_mail='1800013070@pku.edu.cn')
        u.sha256_password = "123456"
        u.save()

        # 方法错误
        response = self.client.get('/user/login')
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 600)

        # 参数错误
        response = self.client.post('/user/login', {'password':'123456'})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 700)

        # 成功
        response = self.client.post('/user/login', {'email':'1800013070', 'password': '123456'})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

    def test_zhuye(self):
        u = User.objects.create_user(username='test3', password='123456', pku_mail='1800013070@pku.edu.cn')
        u.sha256_password = "123456"
        u.save()

        #未登录
        response = self.client.post('/user/zhuye')
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 600)

        response = self.client.post('/user/login', {'email': '1800013070', 'password': '123456'})
        #正确
        response = self.client.post('/user/zhuye')
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 600)

    def test_change_password(self):
        u = User.objects.create_user(username='test4', password='123456', pku_mail='1800013070@pku.edu.cn')
        u.sha256_password = "123456"
        u.save()

        #未登录
        response = self.client.post('/user/profile/edit', {"oldpass":"123456", "newpass": "1234567"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 600)

        response = self.client.post('/user/login', {'email': '1800013070', 'password': '123456'})

        #成功
        response = self.client.post('/user/profile/edit', {"oldpass": "123456", "newpass": "1234567"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

        pass

    def test_password(self):
        u = User.objects.create_user(username='test5', password='123456', pku_mail='1800013070@pku.edu.cn')
        u.sha256_password = "123456"
        u.save()

        response = self.client.post('/user/password', {"email":"1800013070"})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

        verification_code = Verification.objects.get(pku_mail='1800013044@pku.edu.cn').verification_code

        response = self.client.post('/user/password', {'email': "1800013044", 'password': "1234567",
                                                       'verificationCode':verification_code})
        self.assertEqual(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)


