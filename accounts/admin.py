from django.contrib import admin

from .models import Profile, User
from django.contrib import admin

admin.site.register(User)
admin.site.register(Profile)
