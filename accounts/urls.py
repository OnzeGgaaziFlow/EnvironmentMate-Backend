from django.urls import path
from accounts import views

urlpatterns = [
    # path(
    #     "signup-req",
    #     views.SignUpRequestData.as_view({"post": "create", "get": "list"}),
    #     name="signup_request",
    # ),
    # path(
    #     "signup-accept",
    #     views.SignUpRequestAccept.as_view(),
    #     name="signup_accept",
    # ),
    path("test", views.TestView.as_view()),
]
