from django.contrib import auth
from django.contrib.auth import backends
from .models import User


class AuthCodeBackend(backends.ModelBackend):
    # def authenticate(self, request, **kwargs):
    #     email = kwargs["username"]
    #     password = kwargs["password"]
    #     try:
    #         user = User.objects.get(email=email)
    #         if user.check_password(password):
    #             return user
    #     except User.DoesNotExist:
    #         pass
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if username is None or password is None:
            return
        try:
            user = User._default_manager.get_by_natural_key(username)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
