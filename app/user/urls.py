# user/urls.py
from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register_user'),
    path('confirm/',
         views.ConfirmUserRegistrationView.as_view(),
         name='confirm_user_registration'),
    path('authenticate/',
         views.AuthenticateUserView.as_view(),
         name='authenticate_user'),
    path('password-reset/initiate/',
         views.InitiatePasswordResetView.as_view(),
         name='initiate_password_reset'),
    path('password-reset/complete/',
         views.CompletePasswordResetView.as_view(),
         name='complete_password_reset'),
    path('<int:id>/', views.GetUserByIdView.as_view(), name='get_user_by_id'),
    path('<int:id>/update/',
         views.UpdateUserView.as_view(),
         name='update_user'),
]
