from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Notification


@login_required
def notifications_view(request):
    notifications = request.user.notifications.all()
    
    return render(request, 'notifications/notifications.html', {
        'notifications': notifications
    })


@login_required
def api_unread_count(request):
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': unread_count})


@login_required
def api_recent_notifications(request):
    # Get 5 most recent notifications
    notifications = request.user.notifications.all()[:5]
    
    notification_data = []
    for notification in notifications:
        notification_data.append({
            'id': notification.id,
            'sender_id': notification.sender.id,
            'sender_username': notification.sender.username,
            'sender_avatar': notification.sender.profile.profile_picture.url if notification.sender.profile.profile_picture else None,
            'notification_type': notification.notification_type,
            'text': notification.text,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%B %d, %Y, %I:%M %p'),
            'related_object_id': notification.related_object_id
        })
    
    return JsonResponse({'notifications': notification_data})


@login_required
@require_POST
def api_mark_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id, recipient=request.user)
        notification.mark_as_read()
        
        return JsonResponse({
            'status': 'success',
            'notification_id': notification.id,
            'unread_count': request.user.notifications.filter(is_read=False).count()
        })
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def api_mark_all_read(request):
    try:
        unread_notifications = request.user.notifications.filter(is_read=False)
        for notification in unread_notifications:
            notification.mark_as_read()
        
        return JsonResponse({
            'status': 'success',
            'unread_count': 0
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})