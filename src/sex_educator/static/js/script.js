// Sex Education Chatbot Frontend JavaScript

class ChatInterface {
    constructor() {
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.chatMessages = document.getElementById('chatMessages');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.charCount = document.getElementById('charCount');
        this.infoPanel = document.getElementById('infoPanel');
        
        this.isWaitingForResponse = false;
        this.messageHistory = [];
        
        this.initializeEventListeners();
        this.autoResizeTextarea();
        this.checkHealth();
    }
    
    initializeEventListeners() {
        // Send message on button click
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Send message on Enter key (Shift+Enter for new line)
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Character count update
        this.messageInput.addEventListener('input', () => {
            this.updateCharCount();
            this.autoResizeTextarea();
        });
        
        // Disable send button when no text
        this.messageInput.addEventListener('input', () => {
            this.sendBtn.disabled = !this.messageInput.value.trim();
        });
        
        // Initial button state
        this.sendBtn.disabled = true;
    }
    
    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = count;
        
        if (count > 450) {
            this.charCount.style.color = '#e74c3c';
        } else if (count > 400) {
            this.charCount.style.color = '#f39c12';
        } else {
            this.charCount.style.color = '#7f8c8d';
        }
    }
    
    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.updateStatus('Ready to help', true);
            } else {
                this.updateStatus('Connection issues', false);
            }
        } catch (error) {
            console.error('Health check failed:', error);
            this.updateStatus('Connection issues', false);
        }
    }
    
    updateStatus(text, isOnline) {
        const statusText = document.querySelector('.status-text');
        const statusDot = document.querySelector('.status-dot');
        
        if (statusText) statusText.textContent = text;
        if (statusDot) {
            statusDot.className = `status-dot ${isOnline ? 'online' : 'offline'}`;
        }
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || this.isWaitingForResponse) {
            return;
        }
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageHistory.push({ role: 'user', content: message });
        
        // Clear input
        this.messageInput.value = '';
        this.updateCharCount();
        this.autoResizeTextarea();
        
        // Show typing indicator
        this.showTypingIndicator();
        this.isWaitingForResponse = true;
        this.sendBtn.disabled = true;
        
        try {
            // Send to backend
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            if (data.status === 'success') {
                // Add bot response
                this.addMessage(data.response, 'bot');
                this.messageHistory.push({ role: 'assistant', content: data.response });
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            
            let errorMessage = 'Sorry, I encountered an error. Please try again.';
            
            if (error.message.includes('Failed to fetch')) {
                errorMessage = 'Connection lost. Please check your internet connection and try again.';
                this.updateStatus('Connection lost', false);
            }
            
            this.addMessage(errorMessage, 'bot', true);
        } finally {
            this.isWaitingForResponse = false;
            this.sendBtn.disabled = !this.messageInput.value.trim();
        }
    }
    
    addMessage(content, sender, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                ${sender === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-heart"></i>'}
            </div>
            <div class="message-content">
                <div class="message-bubble ${isError ? 'error-message' : ''}">
                    ${this.formatMessage(content)}
                </div>
                <div class="message-time">${timeString}</div>
            </div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Add animation
        requestAnimationFrame(() => {
            messageDiv.style.opacity = '0';
            messageDiv.style.transform = 'translateY(20px)';
            requestAnimationFrame(() => {
                messageDiv.style.transition = 'all 0.5s ease-out';
                messageDiv.style.opacity = '1';
                messageDiv.style.transform = 'translateY(0)';
            });
        });
    }
    
    formatMessage(content) {
        // Convert line breaks to HTML
        let formatted = content.replace(/\n/g, '<br>');
        
        // Convert **bold** to <strong>
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert *italic* to <em>
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert numbered lists
        formatted = formatted.replace(/^\d+\.\s/gm, '• ');
        
        // Convert bullet points
        formatted = formatted.replace(/^\*\s/gm, '• ');
        
        // Wrap in paragraphs if multiple lines
        if (formatted.includes('<br>')) {
            const paragraphs = formatted.split('<br><br>');
            formatted = paragraphs.map(p => `<p>${p.replace(/<br>/g, '<br>')}</p>`).join('');
        } else {
            formatted = `<p>${formatted}</p>`;
        }
        
        return formatted;
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'block';
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    async resetConversation() {
        if (this.isWaitingForResponse) {
            return;
        }
        
        if (!confirm('Are you sure you want to start a new conversation? This will clear all messages.')) {
            return;
        }
        
        this.showLoading();
        
        try {
            const response = await fetch('/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                // Clear chat messages except welcome message
                const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
                this.chatMessages.innerHTML = '';
                if (welcomeMessage) {
                    this.chatMessages.appendChild(welcomeMessage);
                }
                
                this.messageHistory = [];
                this.updateStatus('Ready to help', true);
            }
        } catch (error) {
            console.error('Reset failed:', error);
            alert('Failed to reset conversation. Please refresh the page.');
        } finally {
            this.hideLoading();
        }
    }
    
    toggleInfo() {
        this.infoPanel.classList.toggle('show');
    }
    
    sendQuickMessage(message) {
        this.messageInput.value = message;
        this.updateCharCount();
        this.sendBtn.disabled = false;
        this.sendMessage();
    }
    
    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }
    
    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }
}

// Global functions for HTML onclick handlers
let chatInterface;

function sendMessage() {
    if (chatInterface) {
        chatInterface.sendMessage();
    }
}

function resetConversation() {
    if (chatInterface) {
        chatInterface.resetConversation();
    }
}

function toggleInfo() {
    if (chatInterface) {
        chatInterface.toggleInfo();
    }
}

function sendQuickMessage(message) {
    if (chatInterface) {
        chatInterface.sendQuickMessage(message);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    chatInterface = new ChatInterface();
    
    // Add CSS for error messages
    const style = document.createElement('style');
    style.textContent = `
        .error-message {
            background: #fee !important;
            border-color: #f5c6c6 !important;
            color: #721c24 !important;
        }
        
        .status-dot.offline {
            background: #e74c3c !important;
        }
        
        .status-dot.online {
            background: #27ae60 !important;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        .shake {
            animation: shake 0.5s ease-in-out;
        }
    `;
    document.head.appendChild(style);
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && chatInterface) {
        chatInterface.checkHealth();
    }
});

// Handle online/offline status
window.addEventListener('online', () => {
    if (chatInterface) {
        chatInterface.updateStatus('Back online', true);
        chatInterface.checkHealth();
    }
});

window.addEventListener('offline', () => {
    if (chatInterface) {
        chatInterface.updateStatus('No internet connection', false);
    }
});