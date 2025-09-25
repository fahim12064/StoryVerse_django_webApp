// JavaScript for notifications functionality

document.addEventListener('DOMContentLoaded', function() {
    // Connect to WebSocket for real-time notifications
    connectNotificationWebSocket();
    
    // Initialize notification actions
    initNotificationActions();
    
    // Update notification count periodically
    updateNotificationCount();
    setInterval(updateNotificationCount, 60000); // Update every minute
});

// Connect to WebSocket for real-time notifications
function connectNotificationWebSocket() {
    const userId = document.querySelector('meta[name="user-id"]');
    
    if (userId) {
        const notificationSocket = new WebSocket(
            'ws://' + window.location.host + '/ws/notifications/'
        );
        
        notificationSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            
            if (data.type === 'notification') {
                handleNewNotification(data.notification_data);
            }
        };
        
        notificationSocket.onclose = function(e) {
            console.error('Notification socket closed unexpectedly. Attempting to reconnect...');
            setTimeout(() => {
                connectNotificationWebSocket();
            }, 5000);
        };
        
        notificationSocket.onerror = function(error) {
            console.error('Notification socket error:', error);
        };
    }
}

// Handle new notification
function handleNewNotification(notificationData) {
    // Update notification count
    const notificationBadge = document.getElementById('notification-badge');
    if (notificationBadge) {
        const currentCount = parseInt(notificationBadge.textContent) || 0;
        notificationBadge.textContent = currentCount + 1;
        notificationBadge.classList.remove('hidden');
        notificationBadge.classList.add('notification-badge');
    }
    
    // Add to notification dropdown
    const notificationDropdown = document.getElementById('notification-dropdown');
    if (notificationDropdown) {
        const notificationItem = createNotificationItem(notificationData);
        
        // Add to the top of the list
        const firstItem = notificationDropdown.querySelector('.notification-item');
        if (firstItem) {
            notificationDropdown.insertBefore(notificationItem, firstItem);
        } else {
            notificationDropdown.appendChild(notificationItem);
        }
        
        // Show toast notification
        showToast(notificationData.text, 'info');
    }
}

// Create notification item element
function createNotificationItem(notificationData) {
    const item = document.createElement('a');
    item.className = 'notification-item block px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700 border-b border-gray-200 dark:border-gray-700';
    item.href = '#';
    
    // Determine notification icon
    let iconClass = 'fa-bell';
    if (notificationData.notification_type === 'follow') {
        iconClass = 'fa-user-plus';
    } else if (notificationData.notification_type === 'like') {
        iconClass = 'fa-heart';
    } else if (notificationData.notification_type === 'comment') {
        iconClass = 'fa-comment';
    } else if (notificationData.notification_type === 'reply') {
        iconClass = 'fa-reply';
    }
    
    // Determine notification link
    let link = '#';
    if (notificationData.related_object_id) {
        if (notificationData.notification_type === 'like' || notificationData.notification_type === 'comment') {
            link = `/post/${notificationData.related_object_id}/`;
        } else if (notificationData.notification_type === 'reply') {
            link = `/post/${notificationData.related_object_id}/#comment-${notificationData.id}`;
        }
    }
    
    item.href = link;
    
    // Create notification content
    item.innerHTML = `
        <div class="flex items-start">
            <div class="flex-shrink-0">
                <div class="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                    <i class="fas ${iconClass} text-blue-600 dark:text-blue-400"></i>
                </div>
            </div>
            <div class="ml-3 flex-1">
                <p class="text-sm font-medium text-gray-900 dark:text-white">${notificationData.sender_username}</p>
                <p class="text-sm text-gray-500 dark:text-gray-400">${notificationData.text}</p>
                <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">${formatDate(notificationData.created_at)}</p>
            </div>
            ${!notificationData.is_read ? '<div class="flex-shrink-0"><span class="w-2 h-2 rounded-full bg-blue-500 inline-block"></span></div>' : ''}
        </div>
    `;
    
    return item;
}

// Initialize notification actions
function initNotificationActions() {
    // Mark notification as read
    const markReadButtons = document.querySelectorAll('.mark-notification-read');
    markReadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const notificationId = this.getAttribute('data-notification-id');
            markNotificationRead(notificationId);
        });
    });
    
    // Mark all notifications as read
    const markAllReadButton = document.getElementById('mark-all-notifications-read');
    if (markAllReadButton) {
        markAllReadButton.addEventListener('click', function(e) {
            e.preventDefault();
            markAllNotificationsRead();
        });
    }
}

// Mark notification as read
function markNotificationRead(notificationId) {
    fetch('/notifications/api/mark-read/' + notificationId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update notification count
            const notificationBadge = document.getElementById('notification-badge');
            if (notificationBadge) {
                const newCount = data.unread_count;
                if (newCount > 0) {
                    notificationBadge.textContent = newCount;
                } else {
                    notificationBadge.classList.add('hidden');
                }
            }
            
            // Update notification item
            const notificationItem = document.querySelector(`.notification-item[data-notification-id="${notificationId}"]`);
            if (notificationItem) {
                const unreadIndicator = notificationItem.querySelector('.bg-blue-500');
                if (unreadIndicator) {
                    unreadIndicator.remove();
                }
            }
            
            showToast('Notification marked as read', 'success');
        } else {
            showToast(data.message || 'Failed to mark notification as read', 'error');
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
        showToast('An error occurred', 'error');
    });
}

// Mark all notifications as read
function markAllNotificationsRead() {
    fetch('/notifications/api/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update notification count
            const notificationBadge = document.getElementById('notification-badge');
            if (notificationBadge) {
                notificationBadge.classList.add('hidden');
            }
            
            // Update all notification items
            const unreadIndicators = document.querySelectorAll('.notification-item .bg-blue-500');
            unreadIndicators.forEach(indicator => {
                indicator.remove();
            });
            
            showToast('All notifications marked as read', 'success');
        } else {
            showToast(data.message || 'Failed to mark notifications as read', 'error');
        }
    })
    .catch(error => {
        console.error('Error marking all notifications as read:', error);
        showToast('An error occurred', 'error');
    });
}

// Update notification count
function updateNotificationCount() {
    fetch('/notifications/api/unread-count/', {
        method: 'GET',
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        const notificationBadge = document.getElementById('notification-badge');
        if (notificationBadge) {
            if (data.unread_count > 0) {
                notificationBadge.textContent = data.unread_count;
                notificationBadge.classList.remove('hidden');
            } else {
                notificationBadge.classList.add('hidden');
            }
        }
    })
    .catch(error => {
        console.error('Error updating notification count:', error);
    });
}

// Get CSRF token
function getCsrfToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    return csrfToken ? csrfToken.getAttribute('content') : '';
}