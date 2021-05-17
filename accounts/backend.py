from django.contrib import auth
from django.contrib.auth import backends
from .models import User


class AuthCodeBackend(backends.ModelBackend):
    def authenticate(self, request, **kwargs):
        email = kwargs["email"]
        password = kwargs["password"]
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass
