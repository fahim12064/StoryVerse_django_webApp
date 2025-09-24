from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Post, Category, Subcategory, Comment, Like
from .forms import PostForm, CommentForm
from django.contrib.auth.models import User



def home(request):
    posts = Post.objects.filter(is_published=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for sidebar
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'blog/home.html', context)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, is_published=True)
    
    # Get all comments for this post, ordered by creation time
    comments = post.comments.all().order_by('created_at')
    
    # Check if current user liked this post
    is_liked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(post=post, user=request.user).exists()
    
    # Comment form
    comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'is_liked': is_liked,
        'comment_form': comment_form,
    }
    return render(request, 'blog/post_detail.html', context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            # Award points for creating a post
            request.user.profile.points += 10
            request.user.profile.save()
            
            messages.success(request, 'Your post has been created successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    return render(request, 'blog/create_post.html', {'form': form})


@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your post has been updated successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Your post has been deleted successfully!')
        return redirect('home')
    
    return render(request, 'blog/delete_post.html', {'post': post})


def category_posts(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    posts = Post.objects.filter(category=category, is_published=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for sidebar
    categories = Category.objects.all()
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'blog/category_posts.html', context)


def subcategory_posts(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, pk=subcategory_id)
    posts = Post.objects.filter(subcategory=subcategory, is_published=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for sidebar
    categories = Category.objects.all()
    
    context = {
        'subcategory': subcategory,
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'blog/subcategory_posts.html', context)


def search_posts(request):
    query = request.GET.get('q', '')
    posts = Post.objects.none()
    
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) | 
            Q(author__username__icontains=query),
            is_published=True
        ).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for sidebar
    categories = Category.objects.all()
    
    context = {
        'query': query,
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'blog/search_results.html', context)


@login_required
@require_POST
def add_comment(request):
    post_id = request.POST.get('post_id')
    content = request.POST.get('content')
    parent_id = request.POST.get('parent_id', None)
    
    if not post_id or not content:
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'})
    
    try:
        post = Post.objects.get(id=post_id)
        author = request.user
        
        if parent_id:
            parent = Comment.objects.get(id=parent_id)
            comment = Comment.objects.create(post=post, author=author, content=content, parent=parent)
            
            # Create notification for reply
            if parent.author != author:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=parent.author,
                    sender=author,
                    notification_type='reply',
                    text=f'{author.username} replied to your comment',
                    related_object_id=comment.id
                )
        else:
            comment = Comment.objects.create(post=post, author=author, content=content)
            
            # Create notification for comment
            if post.author != author:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=post.author,
                    sender=author,
                    notification_type='comment',
                    text=f'{author.username} commented on your post',
                    related_object_id=comment.id
                )
        
        # Update points
        author.profile.points += 3
        author.profile.save()
        
        return JsonResponse({
            'status': 'success',
            'comment_id': comment.id,
            'author': comment.author.username,
            'author_id': comment.author.id,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%B %d, %Y, %I:%M %p'),
            'parent_id': comment.parent.id if comment.parent else None,
            'avatar': comment.author.profile.profile_picture.url if comment.author.profile.profile_picture else None
        })
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Post not found'})
    except Comment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Parent comment not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def like_post(request):
    post_id = request.POST.get('post_id')
    
    if not post_id:
        return JsonResponse({'status': 'error', 'message': 'Missing post ID'})
    
    try:
        post = Post.objects.get(id=post_id)
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        
        if created:
            # Update points
            post.author.profile.points += 2
            post.author.profile.save()
            
            # Create notification
            if post.author != request.user:
                from notifications.models import Notification
                Notification.objects.create(
                    recipient=post.author,
                    sender=request.user,
                    notification_type='like',
                    text=f'{request.user.username} liked your post',
                    related_object_id=post.id
                )
            
            return JsonResponse({
                'status': 'success',
                'message': 'You liked this post',
                'likes_count': post.likes.count()
            })
        else:
            return JsonResponse({
                'status': 'info',
                'message': 'You already liked this post',
                'likes_count': post.likes.count()
            })
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Post not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
@require_POST
def unlike_post(request):
    post_id = request.POST.get('post_id')
    
    if not post_id:
        return JsonResponse({'status': 'error', 'message': 'Missing post ID'})
    
    try:
        post = Post.objects.get(id=post_id)
        deleted, _ = Like.objects.filter(post=post, user=request.user).delete()
        
        if deleted:
            # Update points
            post.author.profile.points = max(0, post.author.profile.points - 2)
            post.author.profile.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'You unliked this post',
                'likes_count': post.likes.count()
            })
        else:
            return JsonResponse({
                'status': 'info',
                'message': 'You did not like this post',
                'likes_count': post.likes.count()
            })
    except Post.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Post not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def leaderboard(request):
    # Get top users by points
    top_users = User.objects.annotate(
        post_count=Count('post', filter=Q(post__is_published=True)),
        comment_count=Count('comment')
    ).select_related('profile').order_by('-profile__points')[:20]
    
    # Get categories for sidebar
    categories = Category.objects.all()
    
    context = {
        'top_users': top_users,
        'categories': categories,
    }
    return render(request, 'blog/leaderboard.html', context)