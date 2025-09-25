// JavaScript for messaging functionality

document.addEventListener('DOMContentLoaded', function() {
    // Connect to WebSocket for real-time messaging
    connectChatWebSocket();
    
    // Initialize message form
    initMessageForm();
    
    // Initialize conversation list
    initConversationList();
    
    // Update unread message count periodically
    updateUnreadMessageCount();
    setInterval(updateUnreadMessageCount, 60000); // Update every minute
});

// Connect to WebSocket for real-time messaging
let chatSocket = null;

function connectChatWebSocket() {
    const userId = document.querySelector('meta[name="user-id"]');
    
    if (userId) {
        chatSocket = new WebSocket(
            'ws://' + window.location.host + '/ws/chat/'
        );
        
        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            
            if (data.type === 'new_message') {
                handleNewMessage(data.message_data);
            } else if (data.type === 'message_sent') {
                handleMessageSent(data.message_data);
            }
        };
        
        chatSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly. Attempting to reconnect...');
            setTimeout(() => {
                connectChatWebSocket();
            }, 5000);
        };
        
        chatSocket.onerror = function(error) {
            console.error('Chat socket error:', error);
        };
    }
}

// Handle new message received
function handleNewMessage(messageData) {
    // Update unread message count
    const messageBadge = document.getElementById('message-badge');
    if (messageBadge) {
        const currentCount = parseInt(messageBadge.textContent) || 0;
        messageBadge.textContent = currentCount + 1;
        messageBadge.classList.remove('hidden');
        messageBadge.classList.add('notification-badge');
    }
    
    // Add to conversation list
    const conversationList = document.getElementById('conversation-list');
    if (conversationList) {
        const conversationItem = document.querySelector(`.conversation-item[data-conversation-id="${messageData.conversation_id}"]`);
        
        if (conversationItem) {
            // Update existing conversation
            updateConversationItem(conversationItem, messageData);
        } else {
            // Add new conversation
            const newConversationItem = createConversationItem(messageData);
            conversationList.insertBefore(newConversationItem, conversationList.firstChild);
        }
    }
    
    // Add to message list if in the same conversation
    const currentConversationId = document.querySelector('meta[name="current-conversation-id"]');
    if (currentConversationId && parseInt(currentConversationId.getAttribute('content')) === messageData.conversation_id) {
        addMessageToConversation(messageData);
        
        // Mark messages as read
        markMessagesAsRead(messageData.conversation_id);
    }
    
    // Show toast notification
    showToast(`New message from ${messageData.sender_username}`, 'info');
}

// Handle message sent confirmation
function handleMessageSent(messageData) {
    // Add to message list if in the same conversation
    const currentConversationId = document.querySelector('meta[name="current-conversation-id"]');
    if (currentConversationId && parseInt(currentConversationId.getAttribute('content')) === messageData.conversation_id) {
        addMessageToConversation(messageData);
        
        // Scroll to bottom
        const messageContainer = document.getElementById('message-container');
        if (messageContainer) {
            messageContainer.scrollTop = messageContainer.scrollHeight;
        }
    }
}

// Create conversation item element
function createConversationItem(messageData) {
    const item = document.createElement('a');
    item.className = 'conversation-item block px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700 border-b border-gray-200 dark:border-gray-700';
    item.href = `/messaging/conversation/${messageData.conversation_id}/`;
    item.setAttribute('data-conversation-id', messageData.conversation_id);
    
    // Create conversation content
    item.innerHTML = `
        <div class="flex items-center">
            <div class="flex-shrink-0">
                ${messageData.sender_avatar ? 
                    `<img class="h-12 w-12 rounded-full object-cover" src="${messageData.sender_avatar}" alt="${messageData.sender_username}">` :
                    `<div class="h-12 w-12 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                        <span class="text-gray-600 dark:text-gray-300 font-medium">${messageData.sender_username.charAt(0).toUpperCase()}</span>
                    </div>`
                }
            </div>
            <div class="ml-4 flex-1 min-w-0">
                <div class="flex items-center justify-between">
                    <p class="text-sm font-medium text-gray-900 dark:text-white truncate">${messageData.sender_username}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">${formatDate(messageData.created_at)}</p>
                </div>
                <p class="text-sm text-gray-500 dark:text-gray-400 truncate">${truncateText(messageData.content, 30)}</p>
            </div>
            <div class="ml-2 flex-shrink-0">
                <span class="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
            </div>
        </div>
    `;
    
    return item;
}

// Update conversation item
function updateConversationItem(conversationItem, messageData) {
    const senderName = conversationItem.querySelector('.text-gray-900');
    if (senderName) {
        senderName.textContent = messageData.sender_username;
    }
    
    const messageTime = conversationItem.querySelector('.text-gray-500');
    if (messageTime) {
        messageTime.textContent = formatDate(messageData.created_at);
    }
    
    const messageContent = conversationItem.querySelector('.text-gray-500.truncate');
    if (messageContent) {
        messageContent.textContent = truncateText(messageData.content, 30);
    }
    
    // Add unread indicator if not present
    const unreadIndicator = conversationItem.querySelector('.bg-blue-500');
    if (!unreadIndicator) {
        const indicatorContainer = conversationItem.querySelector('.ml-2.flex-shrink-0');
        if (indicatorContainer) {
            indicatorContainer.innerHTML = '<span class="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>';
        }
    }
    
    // Move to top of list
    const conversationList = document.getElementById('conversation-list');
    if (conversationList) {
        conversationList.insertBefore(conversationItem, conversationList.firstChild);
    }
}

// Add message to conversation
function addMessageToConversation(messageData) {
    const messageContainer = document.getElementById('message-container');
    if (!messageContainer) return;
    
    const messageElement = document.createElement('div');
    messageElement.className = 'flex mb-4';
    
    // Determine if message is from current user
    const currentUserId = document.querySelector('meta[name="user-id"]');
    const isCurrentUser = currentUserId && parseInt(currentUserId.getAttribute('content')) === messageData.sender_id;
    
    if (isCurrentUser) {
        messageElement.classList.add('justify-end');
        messageElement.innerHTML = `
            <div class="max-w-xs lg:max-w-md">
                <div class="bg-blue-500 text-white rounded-lg px-4 py-2">
                    <p>${messageData.content}</p>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">${formatDate(messageData.created_at)}</p>
            </div>
        `;
    } else {
        messageElement.innerHTML = `
            <div class="flex-shrink-0 mr-3">
                ${messageData.sender_avatar ? 
                    `<img class="h-10 w-10 rounded-full object-cover" src="${messageData.sender_avatar}" alt="${messageData.sender_username}">` :
                    `<div class="h-10 w-10 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                        <span class="text-gray-600 dark:text-gray-300 font-medium">${messageData.sender_username.charAt(0).toUpperCase()}</span>
                    </div>`
                }
            </div>
            <div class="max-w-xs lg:max-w-md">
                <div class="bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white rounded-lg px-4 py-2">
                    <p>${messageData.content}</p>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">${formatDate(messageData.created_at)}</p>
            </div>
        `;
    }
    
    messageContainer.appendChild(messageElement);
}

// Initialize message form
function initMessageForm() {
    const messageForm = document.getElementById('message-form');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const recipientId = document.getElementById('recipient-id');
            const messageInput = document.getElementById('message-input');
            
            if (!recipientId || !messageInput || !messageInput.value.trim()) {
                return;
            }
            
            if (chatSocket) {
                chatSocket.send(JSON.stringify({
                    'action': 'send_message',
                    'recipient_id': recipientId.value,
                    'content': messageInput.value.trim()
                }));
                
                // Clear input
                messageInput.value = '';
                messageInput.focus();
            }
        });
    }
}

// Initialize conversation list
function initConversationList() {
    // Load conversations
    loadConversations();
    
    // Setup conversation item clicks
    document.addEventListener('click', function(e) {
        const conversationItem = e.target.closest('.conversation-item');
        if (conversationItem) {
            const conversationId = conversationItem.getAttribute('data-conversation-id');
            if (conversationId) {
                // Remove unread indicator
                const unreadIndicator = conversationItem.querySelector('.bg-blue-500');
                if (unreadIndicator) {
                    unreadIndicator.remove();
                }
            }
        }
    });
}

// Load conversations
function loadConversations() {
    fetch('/messaging/api/conversations/', {
        method: 'GET',
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        const conversationList = document.getElementById('conversation-list');
        if (conversationList && data.conversations) {
            conversationList.innerHTML = '';
            
            if (data.conversations.length === 0) {
                conversationList.innerHTML = '<div class="px-4 py-8 text-center text-gray-500 dark:text-gray-400">No conversations yet</div>';
            } else {
                data.conversations.forEach(conversation => {
                    const conversationItem = document.createElement('a');
                    conversationItem.className = 'conversation-item block px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700 border-b border-gray-200 dark:border-gray-700';
                    conversationItem.href = `/messaging/conversation/${conversation.id}/`;
                    conversationItem.setAttribute('data-conversation-id', conversation.id);
                    
                    // Create conversation content
                    conversationItem.innerHTML = `
                        <div class="flex items-center">
                            <div class="flex-shrink-0">
                                ${conversation.other_participant_avatar ? 
                                    `<img class="h-12 w-12 rounded-full object-cover" src="${conversation.other_participant_avatar}" alt="${conversation.other_participant_username}">` :
                                    `<div class="h-12 w-12 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                                        <span class="text-gray-600 dark:text-gray-300 font-medium">${conversation.other_participant_username.charAt(0).toUpperCase()}</span>
                                    </div>`
                                }
                            </div>
                            <div class="ml-4 flex-1 min-w-0">
                                <div class="flex items-center justify-between">
                                    <p class="text-sm font-medium text-gray-900 dark:text-white truncate">${conversation.other_participant_username}</p>
                                    ${conversation.last_message ? 
                                        `<p class="text-xs text-gray-500 dark:text-gray-400">${formatDate(conversation.last_message.created_at)}</p>` : 
                                        ''
                                    }
                                </div>
                                ${conversation.last_message ? 
                                    `<p class="text-sm text-gray-500 dark:text-gray-400 truncate">${truncateText(conversation.last_message.content, 30)}</p>` : 
                                    `<p class="text-sm text-gray-500 dark:text-gray-400">No messages yet</p>`
                                }
                            </div>
                            ${conversation.unread_count > 0 ? 
                                `<div class="ml-2 flex-shrink-0">
                                    <span class="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
                                </div>` : 
                                ''
                            }
                        </div>
                    `;
                    
                    conversationList.appendChild(conversationItem);
                });
            }
        }
    })
    .catch(error => {
        console.error('Error loading conversations:', error);
    });
}

// Update unread message count
function updateUnreadMessageCount() {
    fetch('/messaging/api/unread-count/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        const messageBadge = document.getElementById('message-badge');
        if (messageBadge) {
            if (data.unread_count > 0) {
                messageBadge.textContent = data.unread_count;
                messageBadge.classList.remove('hidden');
            } else {
                messageBadge.classList.add('hidden');
            }
        }
    })
    .catch(error => {
        console.error('Error updating unread message count:', error);
    });
}

// Mark messages as read
function markMessagesAsRead(conversationId) {
    if (chatSocket) {
        chatSocket.send(JSON.stringify({
            'action': 'mark_read',
            'conversation_id': conversationId
        }));
    }
}

// Get CSRF token
function getCsrfToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    return csrfToken ? csrfToken.getAttribute('content') : '';
}