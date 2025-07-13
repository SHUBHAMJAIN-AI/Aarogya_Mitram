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
        this.historyPanel = document.getElementById('historyPanel');
        this.historyList = document.getElementById('historyList');
        this.historySearch = document.getElementById('historySearch');
        
        // Perplexity-style placeholder suggestions
        this.placeholderSuggestions = [
            'Ask about puberty, relationships, consent, or health...',
            'What is puberty and when does it start?',
            'How do I know if I\'m ready for a relationship?',
            'What does healthy communication look like?',
            'How to talk to parents about body changes?',
            'What are the signs of an unhealthy relationship?',
            'How to set boundaries in relationships?'
        ];
        this.currentPlaceholderIndex = 0;
        
        this.isWaitingForResponse = false;
        this.messageHistory = [];
        
        // Retry configuration
        this.maxRetries = 3;
        this.baseDelay = 2000; // milliseconds
        
        // Mode management
        this.currentMode = 'normal';
        this.availableModes = {};
        
        // Conversation history management
        this.conversationHistory = this.loadConversationHistory();
        this.currentConversationId = this.generateConversationId();
        
        this.initializeEventListeners();
        this.autoResizeTextarea();
        this.checkHealth();
        this.loadModes();
        this.initializeHistorySearch();
        this.startPlaceholderRotation();
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
        
        // Mode selector event listener
        const modeSelector = document.getElementById('modeSelector');
        if (modeSelector) {
            modeSelector.addEventListener('change', (e) => {
                this.switchMode(e.target.value);
            });
        }
    }
    
    initializeHistorySearch() {
        if (this.historySearch) {
            this.historySearch.addEventListener('input', (e) => {
                this.filterHistory(e.target.value);
            });
        }
        this.renderHistoryList();
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
        
        // Save to conversation history
        this.saveToConversationHistory(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        this.updateCharCount();
        this.autoResizeTextarea();
        
        // Show research progress indicators
        this.showResearchProgress();
        this.isWaitingForResponse = true;
        this.sendBtn.disabled = true;
        
        try {
            // Send to backend with retry logic
            const data = await this.fetchWithRetry('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    mode: this.currentMode
                })
            });
            
            // Hide research progress and typing indicator
            this.hideResearchProgress();
            this.hideTypingIndicator();
            
            // Add bot response
            this.addMessage(data.response, 'bot');
            this.messageHistory.push({ role: 'assistant', content: data.response });
            
            // Save to conversation history
            this.saveToConversationHistory(data.response, 'bot');
            
            // Update current mode info
            if (data.current_mode) {
                this.currentMode = data.current_mode;
                this.updateModeDisplay();
            }
            
            // Update suggestions based on response
            this.updateSuggestions(data.suggestions, data.intent);
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideResearchProgress();
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
        
        // Extract and format citations
        formatted = this.formatCitations(formatted);
        
        // Wrap in paragraphs if multiple lines
        if (formatted.includes('<br>')) {
            const paragraphs = formatted.split('<br><br>');
            formatted = paragraphs.map(p => `<p>${p.replace(/<br>/g, '<br>')}</p>`).join('');
        } else {
            formatted = `<p>${formatted}</p>`;
        }
        
        return formatted;
    }
    
    formatCitations(content) {
        // Format citations like [Source: WHO] into clickable elements
        const citationRegex = /\[Source:\s*([^\]]+)\]/g;
        let citationCount = 0;
        const citations = [];
        
        // Extract citations and replace with footnote numbers
        const contentWithFootnotes = content.replace(citationRegex, (match, source) => {
            citationCount++;
            citations.push(source.trim());
            return `<sup class="citation-ref" data-citation="${citationCount}">[${citationCount}]</sup>`;
        });
        
        // Add citations section if citations exist
        if (citations.length > 0) {
            const citationsHtml = citations.map((citation, index) => 
                `<div class="citation-item">
                    <span class="citation-number">[${index + 1}]</span>
                    <span class="citation-source">${citation}</span>
                </div>`
            ).join('');
            
            return contentWithFootnotes + `
                <div class="citations-section">
                    <h4><i class="fas fa-link"></i> Sources</h4>
                    <div class="citations-list">
                        ${citationsHtml}
                    </div>
                </div>`;
        }
        
        return contentWithFootnotes;
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'block';
        this.scrollToBottom();
    }
    
    showResearchProgress() {
        // Hide regular typing indicator
        this.hideTypingIndicator();
        
        // Create research progress indicator
        const progressDiv = document.createElement('div');
        progressDiv.className = 'research-progress';
        progressDiv.id = 'researchProgress';
        
        progressDiv.innerHTML = `
            <div class="message bot-message">
                <div class="message-avatar">
                    <i class="fas fa-heart"></i>
                </div>
                <div class="message-content">
                    <div class="research-status">
                        <div class="progress-step active" data-step="1">
                            <i class="fas fa-search spinning"></i>
                            <span>Researching your question...</span>
                        </div>
                        <div class="progress-step" data-step="2">
                            <i class="fas fa-book-open"></i>
                            <span>Analyzing educational sources</span>
                        </div>
                        <div class="progress-step" data-step="3">
                            <i class="fas fa-brain"></i>
                            <span>Generating culturally sensitive response</span>
                        </div>
                        <div class="progress-step" data-step="4">
                            <i class="fas fa-check-circle"></i>
                            <span>Ready to help</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(progressDiv);
        this.scrollToBottom();
        
        // Simulate progress steps
        this.simulateResearchProgress();
    }
    
    simulateResearchProgress() {
        const steps = document.querySelectorAll('.progress-step');
        let currentStep = 0;
        
        const progressInterval = setInterval(() => {
            if (currentStep < steps.length - 1) {
                // Remove active from current step
                steps[currentStep].classList.remove('active');
                steps[currentStep].classList.add('completed');
                
                // Move to next step
                currentStep++;
                steps[currentStep].classList.add('active');
                
                this.scrollToBottom();
            } else {
                clearInterval(progressInterval);
            }
        }, 800); // Change step every 800ms
        
        // Store interval ID to clear it when response comes
        this.progressInterval = progressInterval;
    }
    
    hideResearchProgress() {
        const progressDiv = document.getElementById('researchProgress');
        if (progressDiv) {
            progressDiv.remove();
        }
        
        // Clear progress interval if running
        if (this.progressInterval) {
            clearInterval(this.progressInterval);
            this.progressInterval = null;
        }
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
                this.currentConversationId = this.generateConversationId();
                this.renderHistoryList();
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
    
    async fetchWithRetry(url, options, attempt = 1) {
        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                return data;
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
            
        } catch (error) {
            const errorStr = error.message.toLowerCase();
            
            // Check if this is a retryable error
            const isRetryable = this.isRetryableError(errorStr);
            
            if (isRetryable && attempt < this.maxRetries) {
                console.log(`Attempt ${attempt} failed, retrying... Error:`, error.message);
                
                // Calculate delay with exponential backoff
                const delay = this.baseDelay * Math.pow(2, attempt - 1);
                
                // Wait before retry
                await new Promise(resolve => setTimeout(resolve, delay));
                
                // Retry
                return this.fetchWithRetry(url, options, attempt + 1);
            } else {
                // Max retries reached or non-retryable error
                console.error(`All ${attempt} attempts failed:`, error);
                throw error;
            }
        }
    }
    
    isRetryableError(errorStr) {
        const retryableIndicators = [
            'overloaded', '503', 'unavailable', 'timeout', 
            'connection', 'network', 'temporary', 'busy',
            'failed to fetch', 'network error'
        ];
        return retryableIndicators.some(indicator => errorStr.includes(indicator));
    }
    
    updateSuggestions(suggestions, intent) {
        const relatedSection = document.getElementById('relatedSection');
        const relatedQuestions = document.getElementById('relatedQuestions');
        
        if (!relatedSection || !relatedQuestions) {
            console.log('Related section elements not found');
            return;
        }
        
        // Hide if no suggestions
        if (!suggestions || (Array.isArray(suggestions) && suggestions.length === 0)) {
            relatedSection.style.display = 'none';
            return;
        }
        
        // Show the related section
        relatedSection.style.display = 'block';
        
        // Clear previous related questions
        relatedQuestions.innerHTML = '';
        
        // Handle both array and object formats
        if (Array.isArray(suggestions)) {
            this.renderSimpleRelated(suggestions, relatedQuestions);
        } else if (typeof suggestions === 'object') {
            this.renderCategorizedRelated(suggestions, relatedQuestions);
        }
    }
    
    renderSimpleRelated(suggestions, container) {
        // Show up to 5 related questions
        suggestions.slice(0, 5).forEach((suggestion) => {
            const relatedItem = document.createElement('div');
            relatedItem.className = 'related-item';
            
            const relatedBtn = document.createElement('button');
            relatedBtn.className = 'related-btn';
            
            const icon = this.getSuggestionIcon(suggestion);
            
            relatedBtn.innerHTML = `
                <i class="${icon}"></i>
                <span>${suggestion}</span>
            `;
            
            // Click sends question to main chat
            relatedBtn.onclick = (e) => {
                e.preventDefault();
                this.sendQuickMessage(suggestion);
            };
            
            relatedItem.appendChild(relatedBtn);
            container.appendChild(relatedItem);
        });
    }
    
    renderCategorizedRelated(suggestionsObj, container) {
        // Flatten all suggestions from categories and show top 5
        const allSuggestions = [];
        Object.entries(suggestionsObj).forEach(([category, suggestions]) => {
            suggestions.slice(0, 2).forEach(suggestion => {
                allSuggestions.push(suggestion);
            });
        });
        
        // Render as simple list
        this.renderSimpleRelated(allSuggestions.slice(0, 5), container);
    }
    
    async createSuggestionWithPreview(suggestionBtn, question, icon, container) {
        // Start by showing question with loading preview
        suggestionBtn.innerHTML = `
            <i class="${icon}"></i>
            <div class="suggestion-content">
                <div class="suggestion-question">${question}</div>
                <div class="suggestion-preview">
                    <span class="preview-loading">Loading...</span>
                </div>
            </div>
        `;
        
        container.appendChild(suggestionBtn);
        
        try {
            // Get answer for preview with retry logic
            const data = await this.fetchWithRetry('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: question,
                    mode: this.currentMode
                })
            });
            
            const fullAnswer = data.response;
            const previewText = this.createPreview(fullAnswer);
            
            // Update with preview - click sends to main chat
            suggestionBtn.innerHTML = `
                <i class="${icon}"></i>
                <div class="suggestion-content">
                    <div class="suggestion-question">${question}</div>
                    <div class="suggestion-preview">
                        <span class="preview-text">${previewText}</span>
                        <span class="expand-dots">...</span>
                    </div>
                </div>
            `;
            
            // Click sends question to main chat (like Perplexity)
            suggestionBtn.onclick = (e) => {
                e.preventDefault();
                this.sendQuickMessage(question);
            };
            
        } catch (error) {
            console.error('Error getting suggestion preview:', error);
            suggestionBtn.innerHTML = `
                <i class="${icon}"></i>
                <div class="suggestion-content">
                    <div class="suggestion-question">${question}</div>
                    <div class="suggestion-preview">
                        <span class="preview-error">Click to ask this question</span>
                    </div>
                </div>
            `;
            
            // Even on error, allow clicking to send question
            suggestionBtn.onclick = (e) => {
                e.preventDefault();
                this.sendQuickMessage(question);
            };
        }
    }
    
    createPreview(fullText) {
        // Split into sentences and take first 2
        const sentences = fullText.split(/[.!?]+/).filter(s => s.trim().length > 0);
        
        if (sentences.length >= 2) {
            return sentences.slice(0, 2).join('. ').trim() + '.';
        } else if (sentences.length === 1) {
            // If only one sentence, truncate at ~100 characters
            const sentence = sentences[0].trim();
            if (sentence.length > 100) {
                return sentence.substring(0, 100).trim();
            }
            return sentence + '.';
        } else {
            // Fallback: truncate at 100 characters
            return fullText.length > 100 ? fullText.substring(0, 100).trim() : fullText;
        }
    }
    
    
    getSuggestionIcon(suggestion) {
        const text = suggestion.toLowerCase();
        
        // Match specific keywords to icons
        if (text.includes('puberty') || text.includes('body') || text.includes('development')) {
            return 'fas fa-seedling';
        } else if (text.includes('relationship') || text.includes('love') || text.includes('partner')) {
            return 'fas fa-heart';
        } else if (text.includes('consent') || text.includes('boundaries') || text.includes('respect')) {
            return 'fas fa-handshake';
        } else if (text.includes('safe') || text.includes('protect') || text.includes('health')) {
            return 'fas fa-shield-alt';
        } else if (text.includes('family') || text.includes('culture') || text.includes('tradition')) {
            return 'fas fa-home';
        } else if (text.includes('doctor') || text.includes('medical') || text.includes('professional')) {
            return 'fas fa-user-md';
        } else if (text.includes('talk') || text.includes('communicate') || text.includes('discuss')) {
            return 'fas fa-comments';
        } else {
            return 'fas fa-arrow-right';
        }
    }
    
    renderCategorizedSuggestions(suggestionsObj, intent, container) {
        let animationDelay = 0;
        
        Object.entries(suggestionsObj).forEach(([category, suggestions]) => {
            // Create category header
            const categoryHeader = document.createElement('div');
            categoryHeader.className = 'suggestion-category';
            categoryHeader.innerHTML = `
                <h4 class="category-title">
                    <i class="${this.getCategoryIcon(category)}"></i>
                    ${category}
                </h4>
            `;
            
            // Add category with animation
            setTimeout(() => {
                container.appendChild(categoryHeader);
                categoryHeader.style.opacity = '0';
                categoryHeader.style.transform = 'translateY(10px)';
                
                setTimeout(() => {
                    categoryHeader.style.transition = 'all 0.3s ease';
                    categoryHeader.style.opacity = '1';
                    categoryHeader.style.transform = 'translateY(0)';
                }, 50);
            }, animationDelay);
            
            animationDelay += 100;
            
            // Add suggestions for this category
            suggestions.slice(0, 3).forEach((suggestion, index) => {
                const suggestionContainer = document.createElement('div');
                suggestionContainer.className = 'suggestion-container';
                
                const suggestionBtn = document.createElement('button');
                suggestionBtn.className = 'suggestion-btn';
                
                // Get appropriate icon based on suggestion content
                const icon = this.getSuggestionIcon(suggestion, intent);
                
                // Create simple suggestion button without preview for categorized view
                suggestionBtn.innerHTML = `
                    <i class="${icon}"></i>
                    <div class="suggestion-content">
                        <div class="suggestion-question">${suggestion}</div>
                    </div>
                `;
                
                // Click sends question to main chat
                suggestionBtn.onclick = (e) => {
                    e.preventDefault();
                    this.sendQuickMessage(suggestion);
                };
                
                suggestionContainer.appendChild(suggestionBtn);
                
                // Add with animation
                setTimeout(() => {
                    container.appendChild(suggestionContainer);
                    suggestionContainer.style.opacity = '0';
                    suggestionContainer.style.transform = 'translateY(10px)';
                    
                    setTimeout(() => {
                        suggestionContainer.style.transition = 'all 0.3s ease';
                        suggestionContainer.style.opacity = '1';
                        suggestionContainer.style.transform = 'translateY(0)';
                    }, 50);
                }, animationDelay);
                
                animationDelay += 80;
            });
        });
    }
    
    renderSimpleSuggestions(suggestions, intent, container) {
        // Legacy support for simple array format
        suggestions.forEach((suggestion, index) => {
            const suggestionContainer = document.createElement('div');
            suggestionContainer.className = 'suggestion-container';
            
            const suggestionBtn = document.createElement('button');
            suggestionBtn.className = 'suggestion-btn';
            
            const icon = this.getSuggestionIcon(suggestion, intent);
            
            // Get answer immediately and show preview
            this.createSuggestionWithPreview(suggestionBtn, suggestion, icon, suggestionContainer);
            
            // Add with slight delay for animation effect
            setTimeout(() => {
                container.appendChild(suggestionContainer);
                suggestionContainer.style.opacity = '0';
                suggestionContainer.style.transform = 'translateY(10px)';
                
                // Animate in
                setTimeout(() => {
                    suggestionContainer.style.transition = 'all 0.3s ease';
                    suggestionContainer.style.opacity = '1';
                    suggestionContainer.style.transform = 'translateY(0)';
                }, 50);
            }, index * 100);
        });
    }
    
    getCategoryIcon(category) {
        const categoryIcons = {
            'Continue Learning': 'fas fa-graduation-cap',
            'Related Topics': 'fas fa-link',
            'Family & Culture': 'fas fa-home',
            'Understanding Basics': 'fas fa-book-open',
            'Health & Wellness': 'fas fa-heartbeat',
            'Education Resources': 'fas fa-library',
            'Getting Started': 'fas fa-play-circle',
            'Practical Guidance': 'fas fa-lightbulb',
            'Self-Assessment': 'fas fa-user-check',
            'Building Foundations': 'fas fa-building',
            'Cultural Considerations': 'fas fa-globe',
            'Communication Skills': 'fas fa-comments',
            'Conflict Resolution': 'fas fa-handshake',
            'Cultural Dynamics': 'fas fa-people-arrows',
            'Relationship Health': 'fas fa-heart',
            'Personal Growth': 'fas fa-seedling',
            'Protection Methods': 'fas fa-shield-alt',
            'Communication': 'fas fa-comment-dots',
            'Emergency Situations': 'fas fa-exclamation-triangle',
            'Testing & Prevention': 'fas fa-stethoscope',
            'Treatment & Support': 'fas fa-medkit',
            'Health Communication': 'fas fa-user-md',
            'Reliable Information': 'fas fa-search',
            'Understanding Consent': 'fas fa-handshake',
            'Consent in Practice': 'fas fa-check-circle',
            'Legal & Cultural Aspects': 'fas fa-gavel',
            'Setting Boundaries': 'fas fa-stop-circle',
            'Respecting Boundaries': 'fas fa-hands-helping',
            'When Boundaries Are Crossed': 'fas fa-exclamation-circle',
            'Consent Basics': 'fas fa-info-circle',
            'Navigating Differences': 'fas fa-route',
            'Family Dynamics': 'fas fa-users',
            'Modern vs Traditional': 'fas fa-balance-scale',
            'Explore Topics': 'fas fa-compass',
            'Resources & Support': 'fas fa-life-ring'
        };
        
        return categoryIcons[category] || 'fas fa-question-circle';
    }
    
    // Conversation History Management
    generateConversationId() {
        return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    loadConversationHistory() {
        try {
            const stored = localStorage.getItem('sexed_conversation_history');
            return stored ? JSON.parse(stored) : {};
        } catch (error) {
            console.error('Error loading conversation history:', error);
            return {};
        }
    }
    
    saveConversationHistory() {
        try {
            localStorage.setItem('sexed_conversation_history', JSON.stringify(this.conversationHistory));
        } catch (error) {
            console.error('Error saving conversation history:', error);
        }
    }
    
    saveToConversationHistory(content, role) {
        const timestamp = new Date().toISOString();
        
        if (!this.conversationHistory[this.currentConversationId]) {
            this.conversationHistory[this.currentConversationId] = {
                id: this.currentConversationId,
                title: this.generateConversationTitle(content, role),
                created: timestamp,
                lastMessage: timestamp,
                messages: []
            };
        }
        
        this.conversationHistory[this.currentConversationId].messages.push({
            role,
            content,
            timestamp
        });
        
        this.conversationHistory[this.currentConversationId].lastMessage = timestamp;
        
        this.saveConversationHistory();
        this.renderHistoryList();
    }
    
    generateConversationTitle(content, role) {
        if (role === 'user') {
            // Use first user message as title, truncated
            return content.length > 50 ? content.substring(0, 50) + '...' : content;
        }
        return 'New Conversation';
    }
    
    renderHistoryList() {
        if (!this.historyList) return;
        
        const conversations = Object.values(this.conversationHistory)
            .sort((a, b) => new Date(b.lastMessage) - new Date(a.lastMessage));
        
        this.historyList.innerHTML = '';
        
        if (conversations.length === 0) {
            this.historyList.innerHTML = '<div class="no-history">No conversations yet</div>';
            return;
        }
        
        conversations.forEach(conv => {
            const convElement = document.createElement('div');
            convElement.className = 'history-item';
            if (conv.id === this.currentConversationId) {
                convElement.classList.add('active');
            }
            
            const lastMessageTime = new Date(conv.lastMessage).toLocaleString();
            const messageCount = conv.messages.length;
            
            convElement.innerHTML = `
                <div class="history-item-content">
                    <h4 class="history-title">${conv.title}</h4>
                    <p class="history-meta">${messageCount} messages • ${lastMessageTime}</p>
                </div>
                <div class="history-actions">
                    <button class="load-conversation-btn" onclick="chatInterface.loadConversation('${conv.id}')">
                        <i class="fas fa-folder-open"></i>
                    </button>
                    <button class="delete-conversation-btn" onclick="chatInterface.deleteConversation('${conv.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            this.historyList.appendChild(convElement);
        });
    }
    
    filterHistory(searchTerm) {
        const historyItems = this.historyList.querySelectorAll('.history-item');
        const term = searchTerm.toLowerCase();
        
        historyItems.forEach(item => {
            const title = item.querySelector('.history-title').textContent.toLowerCase();
            if (title.includes(term)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    loadConversation(conversationId) {
        const conversation = this.conversationHistory[conversationId];
        if (!conversation) return;
        
        // Clear current chat
        this.chatMessages.innerHTML = '';
        this.messageHistory = [];
        
        // Load conversation messages
        conversation.messages.forEach(msg => {
            this.addMessage(msg.content, msg.role === 'user' ? 'user' : 'bot');
            this.messageHistory.push({ role: msg.role, content: msg.content });
        });
        
        this.currentConversationId = conversationId;
        this.renderHistoryList();
        this.toggleHistory(); // Close history panel
    }
    
    deleteConversation(conversationId) {
        if (!confirm('Are you sure you want to delete this conversation?')) {
            return;
        }
        
        delete this.conversationHistory[conversationId];
        this.saveConversationHistory();
        this.renderHistoryList();
        
        // If deleted conversation was current, start new one
        if (conversationId === this.currentConversationId) {
            this.currentConversationId = this.generateConversationId();
        }
    }
    
    toggleHistory() {
        this.historyPanel.classList.toggle('show');
    }
    
    exportHistory() {
        const dataStr = JSON.stringify(this.conversationHistory, null, 2);
        const dataBlob = new Blob([dataStr], {type: 'application/json'});
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'conversation_history.json';
        link.click();
    }
    
    async loadModes() {
        try {
            const response = await fetch('/api/modes');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.availableModes = data.modes;
                this.currentMode = data.current_mode || 'normal';
                this.populateModeSelector();
                this.updateModeDisplay();
            }
        } catch (error) {
            console.error('Error loading modes:', error);
        }
    }
    
    populateModeSelector() {
        const modeSelector = document.getElementById('modeSelector');
        if (!modeSelector) return;
        
        // Clear existing options
        modeSelector.innerHTML = '';
        
        // Add modes as options
        Object.entries(this.availableModes).forEach(([key, mode]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = mode.name;
            if (key === this.currentMode) {
                option.selected = true;
            }
            modeSelector.appendChild(option);
        });
    }
    
    updateModeDisplay() {
        const modeSelector = document.getElementById('modeSelector');
        const modeDescription = document.getElementById('modeDescription');
        
        if (modeSelector) {
            modeSelector.value = this.currentMode;
        }
        
        if (modeDescription && this.availableModes[this.currentMode]) {
            modeDescription.textContent = this.availableModes[this.currentMode].description;
        }
    }
    
    async switchMode(mode) {
        try {
            const response = await fetch('/api/mode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ mode: mode })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.currentMode = data.current_mode;
                this.updateModeDisplay();
                
                // Add a message to chat indicating mode change
                const modeInfo = this.availableModes[this.currentMode];
                this.addMessage(`Switched to ${modeInfo.name}. ${modeInfo.description}`, 'bot');
            } else {
                console.error('Failed to switch mode:', data.error);
                // Reset selector to previous mode
                this.updateModeDisplay();
            }
        } catch (error) {
            console.error('Error switching mode:', error);
            // Reset selector to previous mode
            this.updateModeDisplay();
        }
    }
    
    startPlaceholderRotation() {
        if (!this.messageInput) return;
        
        // Set initial placeholder
        this.messageInput.placeholder = this.placeholderSuggestions[0];
        
        // Rotate placeholder every 3 seconds when input is empty
        setInterval(() => {
            if (this.messageInput.value.trim() === '') {
                this.currentPlaceholderIndex = (this.currentPlaceholderIndex + 1) % this.placeholderSuggestions.length;
                this.messageInput.placeholder = this.placeholderSuggestions[this.currentPlaceholderIndex];
            }
        }, 3000);
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

function switchMode(mode) {
    if (chatInterface) {
        chatInterface.switchMode(mode);
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