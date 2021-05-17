# from django.contrib import auth
# from django.contrib.auth import backends
# from .models import User


# class AuthCodeBackend(backends.ModelBackend):
#     def authenticate(self, request, **kwargs):
#         auth_code = kwargs["username"]
#         password = kwargs["password"]
#         try:
#             user = User.objects.get(auth_code=auth_code)
#             if user.check_password(password):
#                 return user
#         except User.DoesNotExist:
#             pass
