from django.urls import path
import users.views as views


app_name = 'users'
urlpatterns = [
    path('login/', views.UserLogin.as_view(), name='login'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('restore-password/', views.RestorePasswordView.as_view(), name='restore-password'),
    path(r'verify/', views.VerifyView.as_view(), name='verify'),
    path(r'status/', views.otp_status, name='status'),
    path(r'token/', views.otp_token, name='token'),
]
