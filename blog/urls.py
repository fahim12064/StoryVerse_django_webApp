from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('category/<int:category_id>/', views.category_posts, name='category_posts'),
    path('subcategory/<int:subcategory_id>/', views.subcategory_posts, name='subcategory_posts'),
    path('search/', views.search_posts, name='search_posts'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]