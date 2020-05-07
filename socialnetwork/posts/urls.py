from django.urls import path, re_path
from posts.views import (
    LikeCreateDestroyAPIView,
    PostCreateListView,
    LikesPerDayList,
)

urlpatterns = [
    path('likes/', LikeCreateDestroyAPIView.as_view(), name='likes'),
    re_path(r'likes/(?P<post>\d+)', LikeCreateDestroyAPIView.as_view()),
    path('posts/', PostCreateListView.as_view(), name='posts'),
    path('analytics/', LikesPerDayList.as_view(), name='analytics'),
]
