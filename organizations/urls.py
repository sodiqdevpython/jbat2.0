from django.urls import path
from . import views

urlpatterns = [
    # path('', views.PublicView.as_view(), name='public'),
    path('', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('user-detail/<uuid:id>/', views.UserDetail.as_view(), name='user_detail'),
    path('organization-detail/<uuid:id>/', views.OrganizationDetail.as_view(), name='org_detail'),
    path('create-organization-user-profile/', views.CreateUserProfileOrganization.as_view(), name='create_org'),
	
	path('messages/inbox/', views.InboxView.as_view(), name='inbox'),
    path('messages/sent/', views.SentView.as_view(), name='sent'),
    path('messages/compose/', views.ComposeMessageView.as_view(), name='compose'),
    path('messages/<int:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
]