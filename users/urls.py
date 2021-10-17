from django.urls import path

from .views import login_view, register_view, activate_view, logout_view, user_info_view

app_name = 'users'

urlpatterns = [
    # Users index
    path('', user_info_view, name='index'),

    # Authentication
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('activate/<uidb64>/<token>', activate_view, name='activate'),
    path('logout/', logout_view, name='logout'),

    # User info
    path('user_info/', user_info_view, name='user_info'),
    ]
