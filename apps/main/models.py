from __future__ import unicode_literals
from django.db import models
from django.contrib import messages
from datetime import datetime, date, time
import re
import bcrypt
# Create your models here.
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

class UserManager(models.Manager):
    def validate(self, request, post):
        criteria = True
        if len(post.get('name')) < 1 or len(post.get('alias')) < 1 or len(post.get('email')) < 1 or len(post.get('password')) < 1 or len(post.get('password_confirm')) < 1:
            criteria = False
            messages.add_message(request, messages.INFO, "Please fill in all input fields!")
        if not EMAIL_REGEX.match(post.get('email')):
            criteria = False
            messages.add_message(request, messages.INFO, "This email is not a valid email address!")
        if len(post.get('name')) < 3:
            criteria = False
            messages.add_message(request, messages.INFO, "Your name must be longer than 2 characters.")
        if len(post.get('password')) < 8:
            criteria = False
            messages.add_message(request, messages.INFO, "Password must be at least 8 characters long!")
        if len(post.get('password')) < 1:
            criteria = False
            messages.add_message(request, messages.INFO, "Password must have at least 1 character!")
        if post.get('password') != post.get('password_confirm'):
            criteria = False
            messages.add_message(request, messages.INFO, "Your passwords do not match!")
        return(criteria)

    def login_user(self,request, post):
        user = self.filter(email=post.get('email')).first()
        if user and bcrypt.hashpw(post.get('password').encode(), user.password.encode()) == user.password:
            return (True, user)
        messages.add_message(request, messages.INFO, "Your email and password do not match!")
        return (False, 'notuser')

class Increment(models.Model):
    state = models.CharField(max_length=255, default = False)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class User(models.Model):
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    birthday = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()

class Player(models.Model):
    class_type = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default="Alive")
    money = models.IntegerField(default=50)
    health = models.IntegerField(default=3)
    attack = models.IntegerField(default=0)
    medicine = models.IntegerField(default=0)
    coffee = models.IntegerField(default=0)
    user = models.ForeignKey(User, related_name="players")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

class Grave(models.Model):
    user = models.ForeignKey(User, related_name="graves")
    player = models.ForeignKey(Player, related_name="graves")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
