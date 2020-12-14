import os
import json
from django.test import TestCase, Client
from django.http import HttpResponse, JsonResponse, QueryDict
from .models import Post, Comment, Photo, Favor, TextKey
from user.models import User


class PostTests(TestCase):
    # 初始化
    def setUp(self):
        # 添加用户
        u = User.objects.create_user(username='testuser1', password='123456', pku_mail='testuser1@pku.edu.cn')
        u.sha256_password = hash("123456")
        u.save()

        u = User.objects.create_user(username='testuser2', password='123456', pku_mail='testuser2@pku.edu.cn')
        u.sha256_password = hash("123456")
        u.save()
        self.user, self.reader = User.objects.order_by('id')

        # 测试数据库添加数据
        post1 = Post()
        post1.publisher = self.user
        post1.text = '测试1'
        post1.self_favor = True
        post1.is_video = False
        post1.save()
        Favor.objects.create(post=post1, user=self.user)
        Comment.objects.create(post=post1, user=self.user, text='评论0')

        photo1 = Photo()
        photo1.post = post1
        photo1.photo = '/home/ywq/cat1.jpg'
        photo1.save()

        post2 = Post(post_id=post1.post_id + 2)
        post2.publisher = self.user
        post2.text = '测试2'
        post2.save()
        Favor.objects.create(post=post2, user=self.reader)
        Comment.objects.create(post=post2, user=self.user, text='评论1')
        Comment.objects.create(post=post2, user=self.user, text='评论2')

        self.post1 = post1
        self.post2 = post2

    def test_post_post(self):
        # 未登陆
        response = self.client.post('/post/', {'isVideo': 0, 'text': '测试3'})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        print('client receive response', response)
        self.assertEqual(response['code'], 400)

        self.client.post('/user/login', {'email': 'testuser1', 'password': hash('123456')})

        # 参数错误
        response = self.client.post('/post/', {'isVideo': 0, 'test': '测试3'})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        print('client receive response', response)
        self.assertEqual(response['code'], 700)

        response = self.client.post('/post/', {'text': '测试3'})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        print('client receive response', response)
        self.assertEqual(response['code'], 700)

        # 成功
        response = self.client.post('/post/', {'isVideo': 0, 'text': '测试3'})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        print('client receive response', response)
        self.assertEqual(response['code'], 200)
        self.assertTrue(response['data']['postID'] > self.post2.post_id)

        response = self.client.post('/post/', {'isVideo': 0, 'multimediaContent': ['/home/ywq/cat1.jpg']})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        print('client receive response', response)
        self.assertEqual(response['code'], 200)
        self.assertTrue(response['data']['postID'] > self.post2.post_id)