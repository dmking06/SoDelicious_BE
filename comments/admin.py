from django.contrib import admin

from .models import Comment


def approve_comments(request, queryset):
    queryset.update(active=True)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'created_on', 'edited')
    list_filter = ('user', 'recipe', 'created_on')
    search_fields = ('user', 'recipe', 'body')
