from django.urls import path

from .views import CaptchaView, CommentListCreateView, ProfileView

urlpatterns = [
    path("comments/", CommentListCreateView.as_view(), name="comment-list-create"),
    path("captcha/", CaptchaView.as_view(), name="captcha"),
    path("profile/",ProfileView.as_view(),name="profile"),
]