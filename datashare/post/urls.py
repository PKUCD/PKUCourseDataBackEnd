from django.urls import path

from . import views

urlpatterns = [
    path('', views.post),
    path('comments', views.comments),
    path('favor', views.favor),
    path('favor/delete', views.favordelete),
    path('comment', views.comment),
    path('show', views.show),
    path('delete', views.delete),
]