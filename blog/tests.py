from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post, Category, Subcategory, Comment, Like


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Test Category')
        self.subcategory = Subcategory.objects.create(name='Test Subcategory', category=self.category)
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author=self.user,
            category=self.category,
            subcategory=self.subcategory
        )
    
    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.author.username, 'testuser')
        self.assertEqual(self.post.category.name, 'Test Category')
        self.assertEqual(self.post.subcategory.name, 'Test Subcategory')
        self.assertTrue(self.post.is_published)
    
    def test_post_str_method(self):
        self.assertEqual(str(self.post), 'Test Post')
    
    def test_comments_count(self):
        self.assertEqual(self.post.comments_count, 0)
        
        # Add a comment
        Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
        
        self.assertEqual(self.post.comments_count, 1)
    
    def test_likes_count(self):
        self.assertEqual(self.post.likes_count, 0)
        
        # Add a like
        Like.objects.create(
            post=self.post,
            user=self.user
        )
        
        self.assertEqual(self.post.likes_count, 1)


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author=self.user
        )
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test comment'
        )
    
    def test_comment_creation(self):
        self.assertEqual(self.comment.post.title, 'Test Post')
        self.assertEqual(self.comment.author.username, 'testuser')
        self.assertEqual(self.comment.content, 'Test comment')
        self.assertFalse(self.comment.is_reply)
    
    def test_reply_creation(self):
        reply = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='Test reply',
            parent=self.comment
        )
        
        self.assertEqual(reply.parent, self.comment)
        self.assertTrue(reply.is_reply)
    
    def test_comment_str_method(self):
        expected_str = f'Comment by {self.user.username} on {self.post.title}'
        self.assertEqual(str(self.comment), expected_str)


class LikeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author=self.user
        )
        self.like = Like.objects.create(
            post=self.post,
            user=self.user
        )
    
    def test_like_creation(self):
        self.assertEqual(self.like.post.title, 'Test Post')
        self.assertEqual(self.like.user.username, 'testuser')
    
    def test_like_str_method(self):
        expected_str = f'{self.user.username} likes {self.post.title}'
        self.assertEqual(str(self.like), expected_str)
    
    def test_unique_like(self):
        # Trying to create the same like should raise an exception
        with self.assertRaises(Exception):
            Like.objects.create(
                post=self.post,
                user=self.user
            )