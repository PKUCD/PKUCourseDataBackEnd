import os
import json
import threading
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, QueryDict
from .models import Post, Comment, Photo, Favor, TextKey
from user.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect

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


def posts(request):
    # 动态列表
    print('server receive {} {}'.format(request.method, request.get_full_path()))

    if request.method == 'GET':
        # 请求动态列表，GET /posts/?limit&start
        # 检查登陆状态

        try:
            num = int(request.GET.get('limit', default=10))  # 请求动态数量
            start = int(request.GET.get('start', default=0))  # 起始动态id
        except:
            return JsonResponse(gen_response['param_err'])

        post_list = Post.objects.order_by('-post_id')[start:start+num]  # 获取最新动态

        posts = []
        for item in post_list:

            # 加载图片
            multimedia = []
            if item.is_video == False:
                for photo in Photo.objects.filter(post=item):
                    multimedia.append(photo.photo)

            # 判断是否给自己点赞
            user = User.objects.get(id=request.user.id)
            if Favor.objects.filter(post=item).filter(user=user):
                self_favor = 1
            else:
                self_favor = 0

            # 一条摘要动态的数据结构
            publisher_info = {
                'userID': item.publisher.id,
                'username': item.publisher.username,
                'avatar': item.publisher.avatar
            }
            favorcnt = Favor.objects.filter(post=item).count()
            post_info =  {
                'postID': item.post_id,
                'publisher': publisher_info,
                'time': int(item.time.timestamp()*1000),
                'title': item.title,
                'multimediaContent': multimedia,
                'favor': {
                    'self': self_favor,
                    'favorCnt': favorcnt
                }
            }
            posts.append(post_info)

        response = {
            "code": 200,
            "data": {
                "downloadCount": len(posts),
                "posts": posts
            }
        }
        return JsonResponse(response)
    else:
        return JsonResponse(gen_response['method_err'])


def post(request):
#动态获取、添加、删除
    if request.method == 'GET':
    #请求动态，GET /post/?postID&comments
        print('server receive GET', request.get_fukenl_path())

        # 检查登陆状态

        try:
            post_id = int(request.GET.get('postID')) #动态id
            comments_num = int(request.GET.get('comments', default=10)) #评论数量
        except:
            return JsonResponse(gen_response['param_err'])

        # 获取动态数据
        try:
            post = Post.objects.get(post_id=post_id)
        except:
            return JsonResponse(gen_response['post_not_exist'])
        
        # 获取评论区列表
        total_cnt = Comment.objects.filter(post=post).count()
        comments = Comment.objects.filter(post=post)[:comments_num]
        comment_list = []
        for comment in comments:
        
            user = {
                'userID': comment.user.id,
                'username': comment.user.username,
                'avatar': comment.user.avatar
            }
            comment_list.append({
                'commentID': comment.id,
                'user': user,
                'time': int(comment.time.timestamp()*1000),
                'text': comment.text
            })
        if len(comment_list):
            _start = comment_list[0]['commentID']
        else:
            _start = -1
        comment_list_info = {
            'postID': post.post_id,
            'totalCount': total_cnt,
            'downloadCount': len(comment_list),
            'start': _start,
            'comments': comment_list
        }

        publisher_info = {
            'userID': post.publisher.id,
            'username': post.publisher.username,
            'avatar': post.publisher.avatar
        }

        # 加载多媒体内容
        multimedia = []
        if post.is_video == False:
            photos = Photo.objects.filter(post=post)
            for photo_info in photos:
                multimedia.append(photo_info.photo)
        elif post.is_video == True:
            multimedia.append(post.video)

        # 判断是否给自己点赞
        user = User.objects.get(id=request.user.id)
        if Favor.objects.filter(post=post).filter(user=user):
            self_favor = 1
        else:
            self_favor = 0

        favorcnt = Favor.objects.filter(post=post).count()
        post_info =  {
            'postID': post.post_id,
            'publisher': publisher_info,
            'time': int(post.time.timestamp()*1000),
            'title': post.title,
            'text': post.text,
            'isVideo': post.is_video,
            'multimediaContent': multimedia,
            'commentList': comment_list_info,
            'favor': {
                'self': self_favor,
                'favorCnt': favorcnt
            }
        }
        response = {
            "code": 200,
            "data": {
                "downloadCount": 1,
                "post": post_info
            } 
        }
        return JsonResponse(response)
        
    if request.method == 'POST':
        # 发布动态, POST /post/

        # 检查登陆状态

        keywords = request.POST.get('keyword')
        text = request.POST.get('text')
        title = request.POST.get('title')
        isVideo = request.POST.get('isVideo')
        multimediaContent = request.POST.getlist('multimediaContent')

        if isVideo == '1':
            isVideo = True
        elif isVideo == '0':
            isVideo = False
        else:
            return JsonResponse(gen_response['param_err'])

        # 分析参数
        if text is None and title is None and len(multimediaContent) == 0:
            return JsonResponse(gen_response['param_err'])
        if isVideo and len(multimediaContent) == 0:
            return JsonResponse(gen_response['param_err'])


        publisher = User.objects.get(id=request.user.id)

        # 创建数据库动态数据
        post = Post()
        post.publisher = publisher
        post.title = title if not text is None else ""
        post.text = text if not text is None else ""
        post.is_video = isVideo
        if post.is_video:
            post.video = multimediaContent[0]
        post.save()

        # 存储图片
        if isVideo == False:
            for photo_path in multimediaContent:
                photo = Photo()
                photo.photo = photo_path
                photo.post = post
                photo.save()

        for key in keywords:
            TextKey(key=key, post=post).save()

        
        response = {
            "code": 200,
            "data": {
                "postID": post.post_id,
                "time": int(post.time.timestamp()*1000)
            } 
        }
        return JsonResponse(response)

    if request.method == 'DELETE':
    # 删除动态, DELETE /post/?postID=123
        print('server receive DELETE', request.get_full_path())
        
        # 检查登陆状态
        
        DELETE = json.loads(request.body)
        try:
            post_id = int(DELETE.get('postID'))
        except:
            return JsonResponse(gen_response['param_err'])
        
        # 不存在id
        try:
            post = Post.objects.get(post_id=post_id)
        except:
            return JsonResponse(gen_response['post_not_exist'])

        try:
            post.delete()
        except:
            response = {
                "code": 300,
                "data": {
                    "msg": "delete fail"
                }
            }
            return JsonResponse(response)

        response = {
            "code": 200,
            "data": {
                "msg": "delete post successfully"
            }
        }
        return JsonResponse(response)

    if request.method == 'PUT':


        text = request.PUT.get('text')
        title = request.PUT.get('title')
        isVideo = request.PUT.get('isVideo')
        multimediaContent = request.PUT.getlist('multimediaContent')
        post_id = request.PUT.get('postID')
        if isVideo == '1':
            isVideo = True
        elif isVideo == '0':
            isVideo = False
        else:
            return JsonResponse(gen_response['param_err'])

        if text is None and title is None and len(multimediaContent) == 0:
            return JsonResponse(gen_response['param_err'])
        if isVideo and len(multimediaContent) == 0:
            return JsonResponse(gen_response['param_err'])

        publisher = User.objects.get(id=request.user.id)
        if publisher != Post.objects.filter(post_id=post_id).publisher:
            return JsonResponse(gen_response['param_err'])
        post_change = Post.objects.get(post_id=post_id)
        post_change.title = title if not (text is None) else ""
        post_change.text = text if not (text is None) else ""
        post_change.is_video = isVideo
        if post_change.is_video:
            post_change.video = multimediaContent[0]
        post_change.save()

        if isVideo == False:
            for photo_path in multimediaContent:
                photo = Photo()
                photo.photo = photo_path
                photo.post = post_change
                photo.save()

        response = {
            "code": 200,
            "data": {
                "postID": post_change.post_id,
                "time": int(post_change.time.timestamp() * 1000)
            }
        }
        return JsonResponse(response)

    response = gen_response['method_err']
    return JsonResponse(response)

def show(request):
    if request.method == 'GET':
        print('server receive CHANGE', request.get_full_path())

        user_id = request.GET.get('userID')
        user = User.objects.filter(id=user_id)
        user_info = {
            'avatar': user.avatar,
            'pku_mail': user.pku_mail,
        }
        post_list = Post.objects.filter(publisher=user)
        posts_1 = []
        for item in post_list:
            # 一条摘要动态的数据结构
            publisher_info = {
                'userID': item.publisher.id,
                'username': item.publisher.username,
                'avatar': item.publisher.avatar
            }
            post_info = {
                'postID': item.post_id,
                'publisher': publisher_info,
                'time': int(item.time.timestamp() * 1000),
                'title': item.title,
            }
            posts_1.append(post_info)
        posts_2 =[]
        favor_list = Favor.objects.filter(user=user)
        for favor_i in favor_list:
            item = favor_i.post
            publisher_info = {
                'userID': item.publisher.id,
                'username': item.publisher.username,
                'avatar': item.publisher.avatar
            }
            post_info = {
                'postID': item.post_id,
                'publisher': publisher_info,
                'time': int(item.time.timestamp() * 1000),
                'title': item.title,
            }
            posts_2.append(post_info)
        info = {
            'user': user_info,
            'post_list': posts_1,
            'favor_list': posts_2,
        }
        return JsonResponse(info)
    return JsonResponse(gen_response['method_err'])


def search(request):
    # 搜索动态
    if request.method == 'GET':
        # 搜索动态, GET /posts/search/?keyword=大威
        print('server receive GET', request.get_full_path())
        
        # 检查登陆状态
        
        try:
            keyword = request.GET.get('keyword', default=None)
            if keyword is None:
                return JsonResponse(gen_response['param_err'])
        except:
            return JsonResponse(gen_response['param_err'])

        # 获取包含该关键词的post
        keyword_list = TextKey.objects.filter(key=keyword)
        post_list = []
        for key in keyword_list:
            post_list.append(key.post)
        user = User.objects.get(id=request.user.id)
        posts = []
        for item in post_list:

            # 加载图片
            multimedia = []
            if item.is_video == False:
                for photo in Photo.objects.filter(post=item):
                    multimedia.append(photo.photo)
            
            # 判断是否给自己点赞
            if Favor.objects.filter(post=item).filter(user=user):
                self_favor = 1
            else:
                self_favor = 0

            # 一条摘要动态的数据结构
            publisher_info = {
                'userID': item.publisher.id,
                'username': item.publisher.username,
                'avatar': item.publisher.avatar
            }
            favorcnt = Favor.objects.filter(post=item).count()
            post_info =  {
                'postID': item.post_id,
                'publisher': publisher_info,
                'time': int(item.time.timestamp()*1000),
                'text': item.text,
                'multimediaContent': multimedia,
                'favor': {
                    'self': self_favor,
                    'favorCnt': favorcnt
                }
            }
            posts.append(post_info)
        
        response = {
            "code": 200,
            "data": {
                "downloadCount": len(posts),
                "posts": posts
            } 
        }
        return JsonResponse(response)
    
    response = gen_response['method_err']
    return JsonResponse(response)

@csrf_exempt
def comments(request):
    if request.method == 'GET':
    # 获取评论列表, GET /post/comments/?postID=123&limit=10&start=10
        print('server receive GET', request.get_full_path())
        
        # 检查登陆状态
        
        try:
            post_id = int(request.GET.get('postID')) # 评论的动态id
            num = int(request.GET.get('limit', default=10)) # 获取多少个评论
            start = int(request.GET.get('start', default=0)) # 上一次获取的结束评论号
        except:
            return(JsonResponse(gen_response['param_err'])) 
        
        try:
            post = Post.objects.get(post_id=post_id)
        except:
            return JsonResponse(gen_response['post_not_exist']) 
        
        # 获取评论区列表
        total_cnt = Comment.objects.filter(post=post).count()

        comments = Comment.objects.filter(post=post).order_by('-id')[start:start+num]

        comment_list = []
        for comment in comments:
            
            user = {
                'userID': comment.user.id,
                'username': comment.user.username,
                'avatar': comment.user.avatar
            }
            comment_list.append({
                'commentID': comment.id,
                'user': user,
                'time': int(comment.time.timestamp()*1000),
                'text': comment.text
            })
        if len(comment_list):
            _start = comment_list[0]['commentID']
        else:
            _start = -1
        comment_list_info = {
            'postID': post.post_id,
            'totalCount': total_cnt,
            'downloadCount': len(comment_list),
            'start': _start,
            'comments': comment_list
        }

        response = {
            "code": 200,
            "data": {
                "commentList": comment_list_info
            } 
        }
        return JsonResponse(response)
    response = gen_response['method_err']
    return JsonResponse(response)

@csrf_exempt
def favor(request):
    if request.method == 'POST':
    # 点赞, POST /post/favor/?postID=123
        print('server receive POST', request.get_full_path())
        
        # 检查登陆状态
        
        try:
            post_id = int(request.POST.get('postID'))
            user_id = request.user.id
        except:
            return(JsonResponse(gen_response['param_err'])) 
        
        try:
            post = Post.objects.get(post_id=post_id)
        except:
            return JsonResponse(gen_response['post_not_exist'])

        try: 
            user = User.objects.get(id=user_id)
        except:
            return JsonResponse(gen_response['user_not_exist'])
        
        fail = {
            "code": 300,
            "data": {
                "msg": "favored already"
            }
        }
        
        if Favor.objects.filter(post=post).filter(user=user):
            return JsonResponse(fail)
        try:
            Favor(post=post, user=user).save()
        except:
            pass

        return JsonResponse(gen_response['success'])
    elif request.method == 'DELETE':
    # 取消点赞, DELETE /post/favor/?postID=123&userID=123
        print('server receive DELETE', request.get_full_path())
        
        # 检查登陆状态
        
        DELETE = json.loads(request.body)
        try:
            post_id = int(DELETE.get('postID'))
            user_id = int(DELETE.get('userID'))
        except:
            return(JsonResponse(gen_response['param_err'])) 
        
        try:
            post = Post.objects.get(post_id=post_id)
        except:
            return JsonResponse(gen_response['post_not_exist'])

        try: 
            user = User.objects.get(id=user_id)
        except:
            return JsonResponse(gen_response['user_not_exist'])
        
        fail = {
            "code": 300,
            "data": {
                "msg": "never favored"
            }
        }
        try:
            favor = Favor.objects.filter(post=post).filter(user=user)[0]
            favor.delete()
        except:
            return JsonResponse(fail)

        return JsonResponse(gen_response['success'])

    return JsonResponse(gen_response['method_err'])


@csrf_exempt
def comment(request):
    if request.method == 'POST':
    # 评论, POST /post/comment/?postID=123&text=“test”
        print('server receive POST', request.get_full_path())
        
        # 检查登陆状态
        
        try:
            post_id = int(request.POST.get('postID'))
            user_id = request.user.id
            text = request.POST.get('text', default='')
        except:
            return(JsonResponse(gen_response['param_err'])) 

        try:
            post = Post.objects.get(post_id=post_id)
        except:
            return JsonResponse(gen_response['post_not_exist'])

        try: 
            user = User.objects.get(id=user_id)
        except:
            return JsonResponse(gen_response['user_not_exist'])

        comment = Comment()
        comment.post = post
        comment.user = user
        comment.text = text
    
        try:
            comment.save()
        except:
            response = {
                "code": 300,
                "data": {
                    "msg": "comment fail"
                }
            }
            return JsonResponse(response)
        
        return JsonResponse(gen_response['success'])
    response = gen_response['method_err']
    return JsonResponse(response)





