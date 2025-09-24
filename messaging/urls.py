from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_view, name='conversation'),
    path('api/conversations/', views.api_conversations, name='api_conversations'),
    path('api/messages/<int:conversation_id>/', views.api_messages, name='api_messages'),
    path('api/unread-count/', views.api_unread_count, name='api_unread_count'),
]