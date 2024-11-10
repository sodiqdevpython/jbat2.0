from django.urls import path
from . import views

urlpatterns = [
    path('', views.PublicView.as_view(), name='public'),
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout')
]