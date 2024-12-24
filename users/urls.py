from django.urls import path
from .views import UserDashboardView, add, read, OrganizationDetailView, InboxView, SentView, ComposeMessageView, MessageDetailView

urlpatterns = [
    path('dashboard-user/', UserDashboardView.as_view(), name='user_dashboard'),
	path('organization/<uuid:pk>/', OrganizationDetailView.as_view(), name='organization_detail'),
	path('messages/inbox/', InboxView.as_view(), name='inbox2'),
    path('messages/sent/default/', SentView.as_view(), name='sent2'),
    path('messages/compose/default/', ComposeMessageView.as_view(), name='compose2'),
    path('messages/<int:pk>/default/', MessageDetailView.as_view(), name='message-detail2'),
	path('read/', read, name='read'),
	path('add/', add, name='add')
]
