from datetime import datetime, date
from typing import Optional

from django.db.models import Q, Count
from django.utils.timezone import make_aware
from rest_framework import generics, mixins
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from posts.models import Like, Post
from posts.serializers import (
    LikeSerializer,
    LikeAnalyticsSerializer,
    PostSerializer,
    TokenSerializer,
)


class IncorrectParametersException(APIException):
    """
    Represents an exception raised when incorrect params were passed to
    analytics function
    """
    status_code = 400
    default_detail = 'Incorrect parameters'


class TokenAuthView(TokenObtainPairView):
    """
    Represents modified view for JWT
    """
    serializer_class = TokenSerializer


class PostCreateListView(generics.ListCreateAPIView):
    """
    Represents list view for post creating and viewing
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]


class LikeCreateDestroyAPIView(mixins.CreateModelMixin,
                               mixins.DestroyModelMixin,
                               generics.GenericAPIView):
    """
    Represents view for like creating and destroying
    """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]
    # like will be deleted from the specified post
    lookup_field = 'post'

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self):
        """
        Makes queryset limited for current user
        """
        queryset = self.queryset.filter(user=self.request.user)
        return queryset


class LikesPerDayList(generics.ListAPIView):
    """
    Represents view for analytics gathering
    """
    serializer_class = LikeAnalyticsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Gathers analytics about how many likes was made
        """
        def get_date_param(key: str) -> Optional[date]:
            """
            Gets parameter from query string and converts it to date
            :param key: parameter name
            :return: date
            """
            value = self.request.query_params.get(key, None)
            if value:
                try:
                    value = make_aware(
                        datetime.strptime(value, "%Y-%m-%d")
                    ).date()
                except ValueError:
                    value = None

            return value

        q = Q()
        date_from = get_date_param('date_from')
        date_to = get_date_param('date_to')

        if date_from:
            q &= Q(created_at__gte=date_from)

        if date_to:
            q &= Q(created_at__lte=date_to)

        if not len(q):
            raise IncorrectParametersException()

        queryset = (
            Like.objects.filter(q)
            .values('created_at__date')
            .annotate(count=Count('created_at__date'))
            .order_by('created_at__date')
        )
        return queryset
