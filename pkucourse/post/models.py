from django.db import models
from user.models import User
class Data(models.Model):
    id = models.AutoField("id",primary_key=True)
    publisher = models.CharField("publisher",max_length=128)
    title = models.CharField("title",max_length=128)
    url = models.CharField("url",max_length=128)
    time = models.CharField("time",max_length=128)
    likecount = models.IntegerField("likecount")
    favorcount = models.IntegerField("favorcount")

    class meta:
        db_table = "Data"

class Comment(models.Model):
    id = models.AutoField("id",rimary_key=True)
    text = models.CharField("text",max_length=10000)
    name = models.CharField("name",max_length=128)
    dataid = models.ForeignKey(to="Data",to_field=id)

    class meta:
        db_table = "Comment"

class Tag(models.Model):
    text = models.CharField("text",primary_key=True,max_length=128)
    class meta:
        db_table = "Tag"

class Tagrelationship(models.Model):
    id = models.AutoField("id",primary_key=True)
    tag = models.ForeignKey(Tag,on_delete=models.CASCADE)
    data = models.ForeignKey(Data,on_delete=models.CASCADE)

    class meta:
        db_table = "Tagrelationship"

