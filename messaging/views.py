from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Max
from .models import Message, Conversation


@login_required
def inbox(request):
    # Get all conversations for the current user
    conversations = Conversation.objects.filter(participants=request.user).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    # For each conversation, get the last message and unread count
    conversation_data = []
    for conversation in conversations:
        last_message = conversation.last_message
        other_participant = conversation.participants.exclude(id=request.user.id).first()
        
        conversation_data.append({
            'id': conversation.id,
            'other_participant': other_participant,
            'last_message': last_message,
            'unread_count': conversation.unread_count(request.user)
        })
    
    return render(request, 'messaging/inbox.html', {
        'conversations': conversation_data
    })


@login_required
def conversation_view(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    other_participant = conversation.participants.exclude(id=request.user.id).first()
    
    # Get all messages for this conversation
    messages = conversation.messages.all().order_by('created_at')
    
    # Mark all messages as read
    unread_messages = messages.filter(recipient=request.user, is_read=False)
    for message in unread_messages:
        message.mark_as_read()
    
    return render(request, 'messaging/conversation.html', {
        'conversation': conversation,
        'other_participant': other_participant,
        'messages': messages
    })


@login_required
def api_conversations(request):
    # Get all conversations for the current user
    conversations = Conversation.objects.filter(participants=request.user).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    # For each conversation, get the last message and unread count
    conversation_data = []
    for conversation in conversations:
        last_message = conversation.last_message
        other_participant = conversation.participants.exclude(id=request.user.id).first()
        
        conversation_data.append({
            'id': conversation.id,
            'other_participant_id': other_participant.id,
            'other_participant_username': other_participant.username,
            'other_participant_avatar': other_participant.profile.profile_picture.url if other_participant.profile.profile_picture else None,
            'last_message': {
                'id': last_message.id,
                'content': last_message.content,
                'sender_id': last_message.sender.id,
                'created_at': last_message.created_at.strftime('%B %d, %Y, %I:%M %p'),
            } if last_message else None,
            'unread_count': conversation.unread_count(request.user)
        })
    
    return JsonResponse({'conversations': conversation_data})


@login_required
def api_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)
    
    # Get all messages for this conversation
    messages = conversation.messages.all().order_by('created_at')
    
    message_data = []
    for message in messages:
        message_data.append({
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender.id,
            'sender_username': message.sender.username,
            'recipient_id': message.recipient.id,
            'is_read': message.is_read,
            'created_at': message.created_at.strftime('%B %d, %Y, %I:%M %p'),
            'sender_avatar': message.sender.profile.profile_picture.url if message.sender.profile.profile_picture else None
        })
    
    return JsonResponse({'messages': message_data})


@login_required
@require_POST
def api_unread_count(request):
    # Get all conversations for the current user
    conversations = Conversation.objects.filter(participants=request.user)
    
    # Count unread messages
    unread_count = 0
    for conversation in conversations:
        unread_count += conversation.unread_count(request.user)
    
    return JsonResponse({'unread_count': unread_count})


@login_required
@require_POST
def start_conversation(request):
    recipient_id = request.POST.get('recipient_id')
    
    if not recipient_id:
        return JsonResponse({'status': 'error', 'message': 'Recipient ID is required'})
    
    try:
        recipient = User.objects.get(id=recipient_id)
        
        # Check if conversation already exists
        conversations = Conversation.objects.filter(participants=request.user).filter(participants=recipient)
        if conversations.exists():
            conversation = conversations.first()
            return JsonResponse({
                'status': 'success',
                'conversation_id': conversation.id,
                'message': 'Conversation already exists'
            })
        
        # Create new conversation
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, recipient)
        
        return JsonResponse({
            'status': 'success',
            'conversation_id': conversation.id,
            'message': 'Conversation created successfully'
        })
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Recipient not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})