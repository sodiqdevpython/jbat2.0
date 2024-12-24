from django.urls import path
from .views import UserDashboardView, add, read

urlpatterns = [
    path('dashboard-user/', UserDashboardView.as_view(), name='user_dashboard'),
	path('read/', read, name='read'),
	path('add/', add, name='add')
]
