from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_view, name='notifications'),
    path('api/unread-count/', views.api_unread_count, name='api_unread_count'),
    path('api/recent/', views.api_recent_notifications, name='api_recent_notifications'),
    path('api/mark-read/<int:notification_id>/', views.api_mark_read, name='api_mark_read'),
    path('api/mark-all-read/', views.api_mark_all_read, name='api_mark_all_read'),
]