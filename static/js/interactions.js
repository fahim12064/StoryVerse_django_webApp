// JavaScript for user interactions (follow, like, comment)

document.addEventListener('DOMContentLoaded', function() {
    // Initialize follow buttons
    initFollowButtons();
    
    // Initialize like buttons
    initLikeButtons();
    
    // Initialize comment forms
    initCommentForms();
    
    // Initialize reply buttons
    initReplyButtons();
    
    // Initialize follower/following modals
    initFollowerModals();
});

// Initialize follow buttons
function initFollowButtons() {
    const followButtons = document.querySelectorAll('.follow-btn');
    
    followButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const userId = this.getAttribute('data-user-id');
            const isFollowing = this.getAttribute('data-following') === 'true';
            
            if (isFollowing) {
                unfollowUser(userId, this);
            } else {
                followUser(userId, this);
            }
        });
    });
}

// Follow user
function followUser(userId, button) {
    fetch('/accounts/follow/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `user_id=${userId}`,
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update button state
            button.textContent = 'Unfollow';
            button.setAttribute('data-following', 'true');
            button.classList.remove('bg-blue-500', 'hover:bg-blue-600', 'text-white');
            button.classList.add('bg-gray-200', 'hover:bg-gray-300', 'text-gray-800');
            
            // Update followers count
            const followersCount = document.querySelector('.followers-count');
            if (followersCount) {
                followersCount.textContent = data.followers_count;
            }
            
            showToast(data.message, 'success');
        } else {
            showToast(data.message || 'Failed to follow user', 'error');
        }
    })
    .catch(error => {
        console.error('Error following user:', error);
        showToast('An error occurred', 'error');
    });
}

// Unfollow user
function unfollowUser(userId, button) {
    fetch('/accounts/unfollow/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `user_id=${userId}`,
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update button state
            button.textContent = 'Follow';
            button.setAttribute('data-following', 'false');
            button.classList.remove('bg-gray-200', 'hover:bg-gray-300', 'text-gray-800');
            button.classList.add('bg-blue-500', 'hover:bg-blue-600', 'text-white');
            
            // Update followers count
            const followersCount = document.querySelector('.followers-count');
            if (followersCount) {
                followersCount.textContent = data.followers_count;
            }
            
            showToast(data.message, 'success');
        } else {
            showToast(data.message || 'Failed to unfollow user', 'error');
        }
    })
    .catch(error => {
        console.error('Error unfollowing user:', error);
        showToast('An error occurred', 'error');
    });
}

// Initialize like buttons
function initLikeButtons() {
    const likeButtons = document.querySelectorAll('.like-btn');
    
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const postId = this.getAttribute('data-post-id');
            const isLiked = this.getAttribute('data-liked') === 'true';
            
            if (isLiked) {
                unlikePost(postId, this);
            } else {
                likePost(postId, this);
            }
        });
    });
}

// Like post
function likePost(postId, button) {
    fetch('/blog/like/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `post_id=${postId}`,
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update button state
            const icon = button.querySelector('i');
            icon.classList.remove('far');
            icon.classList.add('fas', 'text-red-500');
            button.setAttribute('data-liked', 'true');
            
            // Update likes count
            const likesCount = button.querySelector('.likes-count');
            if (likesCount) {
                likesCount.textContent = data.likes_count;
            }
            
            showToast(data.message, 'success');
        } else {
            showToast(data.message || 'Failed to like post', 'error');
        }
    })
    .catch(error => {
        console.error('Error liking post:', error);
        showToast('An error occurred', 'error');
    });
}

// Unlike post
function unlikePost(postId, button) {
    fetch('/blog/unlike/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `post_id=${postId}`,
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update button state
            const icon = button.querySelector('i');
            icon.classList.remove('fas', 'text-red-500');
            icon.classList.add('far');
            button.setAttribute('data-liked', 'false');
            
            // Update likes count
            const likesCount = button.querySelector('.likes-count');
            if (likesCount) {
                likesCount.textContent = data.likes_count;
            }
            
            showToast(data.message, 'success');
        } else {
            showToast(data.message || 'Failed to unlike post', 'error');
        }
    })
    .catch(error => {
        console.error('Error unliking post:', error);
        showToast('An error occurred', 'error');
    });
}

// Initialize comment forms
function initCommentForms() {
    const commentForms = document.querySelectorAll('.comment-form');
    
    commentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const postId = this.getAttribute('data-post-id');
            const contentInput = this.querySelector('textarea[name="content"]');
            const parentInput = this.querySelector('input[name="parent_id"]');
            
            if (!contentInput || !contentInput.value.trim()) {
                showToast('Please enter a comment', 'warning');
                return;
            }
            
            const content = contentInput.value.trim();
            const parentId = parentInput ? parentInput.value : null;
            
            submitComment(postId, content, parentId, this);
        });
    });
}

// Submit comment
function submitComment(postId, content, parentId, form) {
    fetch('/blog/add-comment/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `post_id=${postId}&content=${encodeURIComponent(content)}${parentId ? `&parent_id=${parentId}` : ''}`,
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Clear form
            const contentInput = form.querySelector('textarea[name="content"]');
            if (contentInput) {
                contentInput.value = '';
            }
            
            // Add comment to the page
            addCommentToPage(data, parentId);
            
            showToast('Comment added successfully', 'success');
        } else {
            showToast(data.message || 'Failed to add comment', 'error');
        }
    })
    .catch(error => {
        console.error('Error adding comment:', error);
        showToast('An error occurred', 'error');
    });
}

// Add comment to page
function addCommentToPage(commentData, parentId) {
    const commentElement = document.createElement('div');
    commentElement.className = 'comment mb-4';
    commentElement.setAttribute('data-comment-id', commentData.id);
    
    if (parentId) {
        // This is a reply
        commentElement.className = 'reply ml-8 pl-4 border-l-2 border-gray-200 dark:border-gray-700';
        
        // Find the parent comment and add the reply
        const parentComment = document.querySelector(`.comment[data-comment-id="${parentId}"]`);
        if (parentComment) {
            const repliesContainer = parentComment.nextElementSibling;
            if (repliesContainer && repliesContainer.classList.contains('replies-container')) {
                repliesContainer.appendChild(commentElement);
            } else {
                // Create replies container if it doesn't exist
                const newRepliesContainer = document.createElement('div');
                newRepliesContainer.className = 'replies-container mt-2';
                newRepliesContainer.appendChild(commentElement);
                parentComment.parentNode.insertBefore(newRepliesContainer, parentComment.nextSibling);
            }
        }
    } else {
        // This is a top-level comment
        const commentsContainer = document.getElementById('comments-container');
        if (commentsContainer) {
            commentsContainer.appendChild(commentElement);
        }
    }
    
    // Create comment content
    commentElement.innerHTML = `
        <div class="flex items-start">
            <div class="flex-shrink-0 mr-3">
                ${commentData.avatar ? 
                    `<img class="h-10 w-10 rounded-full object-cover" src="${commentData.avatar}" alt="${commentData.author}">` :
                    `<div class="h-10 w-10 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                        <span class="text-gray-600 dark:text-gray-300 font-medium">${commentData.author.charAt(0).toUpperCase()}</span>
                    </div>`
                }
            </div>
            <div class="flex-1">
                <div class="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
                    <div class="flex items-center justify-between mb-1">
                        <a href="/accounts/profile/${commentData.author}/" class="font-medium text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400">${commentData.author}</a>
                        <span class="text-xs text-gray-500 dark:text-gray-400">${commentData.created_at}</span>
                    </div>
                    <p class="text-gray-800 dark:text-gray-200">${commentData.content}</p>
                </div>
                <div class="mt-2 flex items-center space-x-4">
                    <button class="reply-btn text-sm text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400" data-comment-id="${commentData.id}">
                        <i class="far fa-reply mr-1"></i> Reply
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Add reply form if this is a top-level comment
    if (!parentId) {
        const replyFormContainer = document.createElement('div');
        replyFormContainer.className = 'reply-form-container hidden mt-2 ml-12';
        replyFormContainer.innerHTML = `
            <form class="comment-form" data-post-id="${commentData.post_id || ''}">
                <input type="hidden" name="parent_id" value="${commentData.id}">
                <div class="mb-2">
                    <textarea name="content" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition" placeholder="Write a reply..."></textarea>
                </div>
                <div class="flex justify-end">
                    <button type="button" class="cancel-reply-btn mr-2 px-3 py-1 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">Cancel</button>
                    <button type="submit" class="px-3 py-1 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600 transition">Reply</button>
                </div>
            </form>
        `;
        
        commentElement.appendChild(replyFormContainer);
    }
    
    // Update comments count
    const commentsCount = document.getElementById('comments-count');
    if (commentsCount) {
        const currentCount = parseInt(commentsCount.textContent) || 0;
        commentsCount.textContent = currentCount + 1;
    }
    
    // Re-initialize reply buttons
    initReplyButtons();
    
    // Re-initialize comment forms
    initCommentForms();
}

// Initialize reply buttons
function initReplyButtons() {
    const replyButtons = document.querySelectorAll('.reply-btn');
    
    replyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const comment = document.querySelector(`.comment[data-comment-id="${commentId}"]`);
            
            if (comment) {
                const replyFormContainer = comment.querySelector('.reply-form-container');
                if (replyFormContainer) {
                    replyFormContainer.classList.toggle('hidden');
                    
                    // Focus on textarea if form is shown
                    if (!replyFormContainer.classList.contains('hidden')) {
                        const textarea = replyFormContainer.querySelector('textarea');
                        if (textarea) {
                            textarea.focus();
                        }
                    }
                }
            }
        });
    });
    
    // Cancel reply buttons
    const cancelReplyButtons = document.querySelectorAll('.cancel-reply-btn');
    cancelReplyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const replyFormContainer = this.closest('.reply-form-container');
            if (replyFormContainer) {
                replyFormContainer.classList.add('hidden');
            }
        });
    });
}

// Initialize follower/following modals
function initFollowerModals() {
    const followersLinks = document.querySelectorAll('.followers-link');
    const followingLinks = document.querySelectorAll('.following-link');
    
    followersLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const username = this.getAttribute('data-username');
            loadFollowers(username);
        });
    });
    
    followingLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const username = this.getAttribute('data-username');
            loadFollowing(username);
        });
    });
}

// Load followers
function loadFollowers(username) {
    fetch(`/accounts/profile/${username}/followers/`, {
        method: 'GET',
        credentials: 'same-origin',
    })
    .then(response => response.text())
    .then(html => {
        const modal = document.createElement('div');
        modal.className = 'modal fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        modal.id = 'followers-modal';
        
        modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full max-h-[80vh] overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white">Followers</h3>
                    <button class="modal-close text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="overflow-y-auto max-h-[60vh]">
                    ${html}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Initialize modal close button
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                document.body.removeChild(modal);
            });
        }
        
        // Close modal when clicking outside
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    })
    .catch(error => {
        console.error('Error loading followers:', error);
        showToast('An error occurred', 'error');
    });
}

// Load following
function loadFollowing(username) {
    fetch(`/accounts/profile/${username}/following/`, {
        method: 'GET',
        credentials: 'same-origin',
    })
    .then(response => response.text())
    .then(html => {
        const modal = document.createElement('div');
        modal.className = 'modal fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50';
        modal.id = 'following-modal';
        
        modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full max-h-[80vh] overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                    <h3 class="text-lg font-medium text-gray-900 dark:text-white">Following</h3>
                    <button class="modal-close text-gray-400 hover:text-gray-500 dark:hover:text-gray-300">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="overflow-y-auto max-h-[60vh]">
                    ${html}
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Initialize modal close button
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                document.body.removeChild(modal);
            });
        }
        
        // Close modal when clicking outside
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    })
    .catch(error => {
        console.error('Error loading following:', error);
        showToast('An error occurred', 'error');
    });
}

// Get CSRF token
function getCsrfToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    return csrfToken ? csrfToken.getAttribute('content') : '';
}