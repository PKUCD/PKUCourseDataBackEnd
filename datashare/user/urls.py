from django.urls import path, include

from . import views

urlpatterns = [
    path('register/validationCode', views.register),
    path('register', views.register_validation),
    path('profile/edit', views.change_password),
    path('login', views.login),
    path('logout', views.logout),
    path('password', views.password),
    path('zhuye', views.zhuye),
]
