from django.contrib import admin

from .models import Comment


def approve_comments(request, queryset):
    queryset.update(active=True)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('profile', 'recipe', 'created_on', 'edited')
    list_filter = ('profile', 'recipe', 'created_on')
    search_fields = ('profile', 'recipe', 'body')
