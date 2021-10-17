from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from recipes.views import landing_page

urlpatterns = [
                  # Admin pages
                  path('admin/', admin.site.urls),

                  # Homepage
                  path('', landing_page, name='landing_page'),

                  # apps
                  path('users/', include('users.urls')),
                  path('recipes/', include('recipes.urls')),
                  path('comments/', include('comments.urls')),

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
