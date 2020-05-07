from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    last_activity = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Last activity',
        blank=True,
        null=True,
    )


class Post(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='User',
    )
    content = models.TextField(
        verbose_name='Content',
    )
    created_at = models.DateTimeField(
        verbose_name='Date created',
        auto_now_add=True,
    )

    def __str__(self):
        return f'{self.user} at {self.created_at.date()}'

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
        ]
        ordering = ['created_at']


class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='User',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Post',
    )
    created_at = models.DateTimeField(
        verbose_name='Date created',
        auto_now_add=True,
    )

    def __str__(self):
        return f'{self.user} to {self.post}'

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['created_at']),
        ]
        ordering = ['created_at']
