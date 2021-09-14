from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from users.views import user_info_view

urlpatterns = [
                  # Admin pages
                  path('admin/', admin.site.urls),

                  # Homepage
                  path('', user_info_view, name='index'),

                  # apps
                  path('users/', include('users.urls')),
                  path('recipes/', include('recipes.urls')),

                  # Password reset
                  path('reset_password/',
                       auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"),
                       name="reset_password"),
                  path('reset_password_sent/',
                       auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_sent.html"),
                       name="password_reset_done"),
                  path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
                          template_name="registration/password_reset_form.html"), name="password_reset_confirm"),
                  path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
                          template_name="registration/password_reset_done.html"), name="password_reset_complete"),

                  ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
