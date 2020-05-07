from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from posts.models import Post, User, Like


admin.site.register(User, UserAdmin)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fields = ('user', 'content', 'created_at')
    readonly_fields = ('user', 'created_at')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    fields = ('user', 'post', 'created_at')
    readonly_fields = ('created_at', )
