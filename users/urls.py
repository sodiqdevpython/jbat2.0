from django.urls import path
from .views import UserDashboardView, add, read, InboxView, SentView, ComposeMessageView, MessageDetailView, UserOrganizationDetailView, EquipmentCreateView, EquipmentUpdateView, UserEquipmentListView, EquipmentDetailView

urlpatterns = [
    path('dashboard-user/', UserDashboardView.as_view(), name='user_dashboard'),
	path('messages/inbox/', InboxView.as_view(), name='inbox2'),
    path('messages/sent/default/', SentView.as_view(), name='sent2'),
    path('messages/compose/default/', ComposeMessageView.as_view(), name='compose2'),
    path('messages/<int:pk>/default/', MessageDetailView.as_view(), name='message-detail2'),
	path('read/', read, name='read'),
	path('add/', add, name='add'),
	path('organization/<uuid:pk>/', UserOrganizationDetailView.as_view(), name='user_org_detail'),
	path('equipment/create/', EquipmentCreateView.as_view(), name='equipment_create'),
    path('equipment/<str:pk>/update/', EquipmentUpdateView.as_view(), name='equipment_update_user'),
	path('equipment-list/', UserEquipmentListView.as_view(), name='user_equipment_list'),
	path('equipment-detail/<str:pk>/', EquipmentDetailView.as_view(), name='eq_detail_user')
]
