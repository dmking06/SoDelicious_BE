from django.urls import path

from . import views

app_name = 'comments'

urlpatterns = [
    # View user comments
    path('', views.MyCommentsView.as_view(), name='my_comments'),
    path('create/<int:recipe_id>', views.create_comment, name='create_comment'),
    path('edit/<int:comment_id>', views.edit_comment, name='edit_comment'),
    path('delete/<int:comment_id>', views.delete_comment, name='delete_comment')
    ]
