from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.Dashboard.as_view(), name='admin_dashboard'),
    path('users/', views.Users.as_view(), name='users'),
    path('worker-group/', views.WorkerGroup.as_view(), name='worker_group'),
    path('search-user/', views.SearchUsers.as_view(), name='search_user'),
    path('page-not-ready/', views.PageIsNotReady.as_view(), name='page_not_ready'),
    path('equipment-list-admin/', views.EquipmentList.as_view(), name='admin_equipment_list'),
    path('material-tecnic-base/', views.MaterialTechnicBase.as_view(), name='material_technic_base'),
    path('organization-list/', views.OrganizationList.as_view(), name='organization_list')
]