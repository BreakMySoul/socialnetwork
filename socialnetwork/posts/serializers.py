from django.contrib.auth.models import update_last_login
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from posts.models import Like, Post, User


class TokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super(TokenSerializer, cls).get_token(user)
        update_last_login(None, user)
        return token


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + (
            'last_login',
            'last_activity',
        )
        read_only_fields = BaseUserSerializer.Meta.read_only_fields + (
            'last_login',
            'last_activity',
        )


class PostSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
    )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        queryset=User.objects.all(),
    )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    class Meta:
        model = Like
        fields = ['user', 'post', 'created_at']


class LikeAnalyticsSerializer(serializers.Serializer):
    created_at__date = serializers.DateField()
    count = serializers.IntegerField()
