from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile, Follow


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.profile = Profile.objects.get(user=self.user)
    
    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.points, 0)
    
    def test_followers_count(self):
        self.assertEqual(self.profile.followers_count, 0)
        
        # Create a follower
        follower = User.objects.create_user(username='follower', password='testpass')
        Follow.objects.create(follower=follower, following=self.user)
        
        self.assertEqual(self.profile.followers_count, 1)
    
    def test_following_count(self):
        self.assertEqual(self.profile.following_count, 0)
        
        # Create a user to follow
        following = User.objects.create_user(username='following', password='testpass')
        Follow.objects.create(follower=self.user, following=following)
        
        self.assertEqual(self.profile.following_count, 1)


class FollowModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass')
        self.user2 = User.objects.create_user(username='user2', password='testpass')
        self.follow = Follow.objects.create(follower=self.user1, following=self.user2)
    
    def test_follow_creation(self):
        self.assertEqual(self.follow.follower.username, 'user1')
        self.assertEqual(self.follow.following.username, 'user2')
    
    def test_unique_follow(self):
        # Trying to create the same follow relationship should raise an exception
        with self.assertRaises(Exception):
            Follow.objects.create(follower=self.user1, following=self.user2)