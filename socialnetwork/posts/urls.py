from django.urls import path, re_path
from posts.views import (
    LikeCreateDestroyAPIView,
    PostCreateList,
    LikesPerDayList,
)

urlpatterns = [
    path('likes/', LikeCreateDestroyAPIView.as_view()),
    re_path(r'likes/(?P<post>\d+)', LikeCreateDestroyAPIView.as_view()),
    path('posts/', PostCreateList.as_view()),
    path('analytics/', LikesPerDayList.as_view()),
]
