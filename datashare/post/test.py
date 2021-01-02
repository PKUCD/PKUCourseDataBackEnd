import os
import json
from django.test import TestCase, Client
from django.http import HttpResponse, JsonResponse, QueryDict
from .models import Post, Comment, Photo, Favor, TextKey
from user.models import User


class PostTests(TestCase):
    def setUp(self):
        u = User.objects.create_user(username='test1', password='123456', pku_mail='test1@pku.edu.cn')
        u.sha256_password = "123456"
        u.save()

        self.user = u

        post1 = Post()
        post1.publisher = self.user
        post1.title = "标题1"
        post1.text = "内容1"
        post1.self_favor = False
        post1.is_video = False
        post1.save()
        Comment.objects.create(post=post1, user=self.user, text='评论1')
        self.post1 = post1

    def test_post_post(self):

        # 登陆问题
        response = self.client.post('/post/', {'isVideo': 0, 'text': '内容2', 'title': '标题2'})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 400)

        # 成功
        self.client.post('/user/login', {'email': 'test1', 'password': '123456'})
        response = self.client.post('/post/', {'isVideo': 0, 'text': '内容3', 'title': '标题3'})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

    def test_get_post(self):

        # 登陆问题
        response = self.client.get('/post/', {'postID': self.post1.post_id})
        self.assertEquals(type(response), JsonResponse)
        self.assertEqual(response['code'], 400)

        self.client.post('/user/login', {'email': 'test1', 'password': '123456'})

        #id不存在
        response = self.client.get('/post/', {'postID': 30})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 300)

        #一切正常
        response = self.client.get('/post/', {'postID':self.post1.post_id})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

    def test_favor(self):

        #直接登陆吧
        self.client.post('/user/login', {'email': 'testuser1', 'password': '123456'})

        #id不正确
        response = self.client.get('/post/favor', {'postID': 200})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 300)

        #成功点赞
        response = self.client.post('/post/favor', {'postID':self.post1.post_id})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

        #重复点赞
        response = self.client.post('/post/favor', {'postID':self.post1.post_id})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 300)

    def test_favordelete(self):

        self.client.post('/user/login', {'email': 'testuser1', 'password': '123456'})

        response = self.client.post('/post/favor/delete', {'postID': self.post1.post_id})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

        #重复删除
        response = self.client.post('/post/favor/delete', {'postID': self.post1.post_id})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 300)

    def test_comment(self):

        self.client.post('/user/login', {'email': 'testuser1', 'password': '123456'})

        #id不存在
        response = self.client.post('/post/comment/', {'postID': 30, 'userID': self.user.id})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 300)

        #正确
        response = self.client.post('/post/comment/', {'postID': self.post1.post_id, 'userID': self.user.id, 'text':'评论'})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

    def test_comments(self):
        self.client.post('/user/login', {'email': 'testuser1', 'password':'123456'})

        # 不正确的动态id
        response = self.client.get('/post/comments/', {'postID': 30})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 300)

        #成功
        response = self.client.get('/post/comments/', {'postID':self.post1.post_id})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

    def test_delete(self):

        #未登录
        response = self.client.get('/post/delete', {'postID': self.post1.post_id})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 400)

        self.client.post('/user/login', {'email': 'test1', 'password': '123456'})

        #不存在这个id
        response = self.client.get('/post/delete', {'postID': 30})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 300)

        response = self.client.get('/post/delete', {'postID': self.post1.post_id})
        self.assertEquals(type(response), JsonResponse)
        response = response.json()
        self.assertEqual(response['code'], 200)

