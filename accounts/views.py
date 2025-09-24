from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from .forms import CustomUserCreationForm, ProfileForm
from .models import Profile, Follow



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    
    # Get user's posts
    from blog.models import Post
    posts = Post.objects.filter(author=user).order_by('-created_at')
    
    # Check if current user is following this profile
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    
    context = {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})


def followers_view(request, username):
    user = get_object_or_404(User, username=username)
    followers = User.objects.filter(following__following=user).annotate(
        mutual_follow=Count('followers', filter=Q(followers__follower=request.user))
    )
    
    return render(request, 'accounts/followers.html', {
        'profile_user': user,
        'followers': followers,
    })


def following_view(request, username):
    user = get_object_or_404(User, username=username)
    following = User.objects.filter(followers__follower=user).annotate(
        mutual_follow=Count('followers', filter=Q(followers__follower=request.user))
    )
    
    return render(request, 'accounts/following.html', {
        'profile_user': user,
        'following': following,
    })


@login_required
@require_POST
def follow_user(request):
    user_id = request.POST.get('user_id')
    try:
        user_to_follow = User.objects.get(id=user_id)
        profile, created = Profile.objects.get_or_create(user=user_to_follow)
        
        # Create follow relationship
        follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        
        if created:
            # Update points
            profile.points += 5
            profile.save()
            
            # Create notification
            from notifications.models import Notification
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow',
                text=f'{request.user.username} started following you'
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'You are now following this user',
                'followers_count': profile.followers.count()
            })
        else:
            return JsonResponse({
                'status': 'info',
                'message': 'You are already following this user',
                'followers_count': profile.followers.count()
            })
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def unfollow_user(request):
    user_id = request.POST.get('user_id')
    try:
        user_to_unfollow = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user_to_unfollow)
        
        # Remove follow relationship
        deleted, _ = Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
        
        if deleted:
            # Update points
            profile.points = max(0, profile.points - 5)
            profile.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'You have unfollowed this user',
                'followers_count': profile.followers.count()
            })
        else:
            return JsonResponse({
                'status': 'info',
                'message': 'You were not following this user',
                'followers_count': profile.followers.count()
            })
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})