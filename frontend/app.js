  // ============= STATE MANAGEMENT =============
class ChatManager {
    constructor() {
        this.sessionId = this.getOrCreateSession();
        this.messages = [];
        this.isLoading = false;
    }

    getOrCreateSession() {
        let sessionId = localStorage.getItem('sessionId');
        if (!sessionId) {
            sessionId = this.generateSessionId();
            localStorage.setItem('sessionId', sessionId);
        }
        return sessionId;
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    addMessage(role, content, metadata = {}) {
        const message = {
            role,
            content,
            timestamp: new Date().toISOString(),
            ...metadata
        };
        this.messages.push(message);
        this.saveSession();
        return message;
    }

    getMessages() {
        return this.messages;
    }

    saveSession() {
        localStorage.setItem(`chat_${this.sessionId}`, JSON.stringify(this.messages));
    }

    loadSession() {
        const saved = localStorage.getItem(`chat_${this.sessionId}`);
        if (saved) {
            try {
                this.messages = JSON.parse(saved);
            } catch (e) {
                console.error('Error loading session:', e);
                this.messages = [];
            }
        }
    }

    clearSession() {
        this.messages = [];
        localStorage.removeItem(`chat_${this.sessionId}`);
    }
}

// ============= UI MANAGER =============
class UIManager {
    constructor() {
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.toastContainer = document.getElementById('toastContainer');
        this.sessionsList = document.getElementById('sessionsList');
        this.headerStatus = document.getElementById('headerStatus');
        this.tokenInfo = document.getElementById('tokenInfo');
    }

    showMessage(role, content, metadata = {}) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${role}`;

        const contentEl = document.createElement('div');
        contentEl.className = 'message-content';
        contentEl.textContent = content;

        messageEl.appendChild(contentEl);

        // Add metadata
        if (metadata.tokens || metadata.chunks || metadata.confidence) {
            const metaEl = document.createElement('div');
            metaEl.className = 'message-meta';
            
            if (role === 'assistant') {
                let metaText = '';
                if (metadata.chunks) {
                    metaText += `📚 ${metadata.chunks} chunk(s) retrieved`;
                }
                if (metadata.confidence) {
                    metaText += ` ${this.getConfidenceBadge(metadata.confidence)}`;
                }
                if (metadata.tokens) {
                    metaText += ` | 📊 ${metadata.tokens} tokens`;
                }
                metaEl.innerHTML = metaText;
            }
            
            messageEl.appendChild(metaEl);
        }

        this.messagesContainer.appendChild(messageEl);
        this.scrollToBottom();
    }

    getConfidenceBadge(confidence) {
        const percent = Math.round(confidence * 100);
        return `<span class="confidence-badge">Confidence: ${percent}%</span>`;
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    showLoading(show = true) {
        if (show) {
            this.loadingOverlay.classList.add('active');
        } else {
            this.loadingOverlay.classList.remove('active');
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        this.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.remove();
        }, 4000);
    }

    clearMessages() {
        this.messagesContainer.innerHTML = `
            <div class="welcome-message">
                <h2>👋 Welcome to GenAI Assistant</h2>
                <p>Ask me questions about our services, features, security, billing, and more.</p>
                <div class="sample-questions">
                    <p><strong>Sample Questions:</strong></p>
                    <button class="sample-btn" onclick="sendMessage('How do I reset my password?')">
                        How do I reset my password?
                    </button>
                    <button class="sample-btn" onclick="sendMessage('What are your subscription plans?')">
                        What are your subscription plans?
                    </button>
                    <button class="sample-btn" onclick="sendMessage('How is my data protected?')">
                        How is my data protected?
                    </button>
                </div>
            </div>
        `;
    }

    updateStatus(status) {
        this.headerStatus.textContent = status;
    }

    updateTokenInfo(tokens) {
        if (tokens) {
            this.tokenInfo.textContent = `Tokens used: ${tokens}`;
        }
    }

    disableInput(disabled = true) {
        this.messageInput.disabled = disabled;
        this.sendBtn.disabled = disabled;
    }

    focusInput() {
        this.messageInput.focus();
    }
}

// ============= API CLIENT =============
class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
    }

    async chat(sessionId, message) {
        try {
            const response = await fetch(`${this.baseURL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    sessionId,
                    message
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || error.error || 'Chat request failed');
            }

            return await response.json();
        } catch (error) {
            throw new Error(`API Error: ${error.message}`);
        }
    }

    async health() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            return response.ok;
        } catch {
            return false;
        }
    }

    async getSession(sessionId) {
        try {
            const response = await fetch(`${this.baseURL}/api/sessions/${sessionId}`);
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to get session: ${error.message}`);
        }
    }

    async clearSession(sessionId) {
        try {
            const response = await fetch(`${this.baseURL}/api/sessions/${sessionId}`, {
                method: 'DELETE'
            });
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to clear session: ${error.message}`);
        }
    }
}

// ============= INITIALIZATION =============
let chatManager;
let uiManager;
let apiClient;

document.addEventListener('DOMContentLoaded', async () => {
    // Initialize managers
    chatManager = new ChatManager();
    uiManager = new UIManager();
    apiClient = new APIClient();

    // Load previous session
    chatManager.loadSession();
    if (chatManager.messages.length === 0) {
        uiManager.clearMessages();
    } else {
        // Display previous messages
        chatManager.messages.forEach(msg => {
            const metadata = {};
            if (msg.tokens) metadata.tokens = msg.tokens;
            if (msg.chunks) metadata.chunks = msg.chunks;
            if (msg.confidence) metadata.confidence = msg.confidence;
            uiManager.showMessage(msg.role, msg.content, metadata);
        });
    }

    // Check API health
    const healthy = await apiClient.health();
    if (healthy) {
        uiManager.updateStatus('✓ Ready to chat');
    } else {
        uiManager.updateStatus('⚠ Connection issue');
        uiManager.showToast('Unable to connect to server', 'error');
    }

    // Setup event listeners
    uiManager.sendBtn.addEventListener('click', handleSend);
    uiManager.messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    uiManager.clearBtn.addEventListener('click', handleClear);
    uiManager.newChatBtn.addEventListener('click', handleNewChat);

    // Focus input
    uiManager.focusInput();
});

// ============= EVENT HANDLERS =============
async function handleSend() {
    const message = uiManager.messageInput.value.trim();

    if (!message) {
        uiManager.showToast('Please enter a message', 'error');
        return;
    }

    if (chatManager.isLoading) {
        return;
    }

    try {
        // Show user message
        uiManager.showMessage('user', message);
        chatManager.addMessage('user', message);

        // Clear input
        uiManager.messageInput.value = '';
        uiManager.disableInput(true);
        uiManager.showLoading(true);
        uiManager.updateStatus('Processing...');

        // Send to API
        const response = await apiClient.chat(chatManager.sessionId, message);

        // Show assistant response
        const metadata = {
            tokens: response.tokensUsed,
            chunks: response.retrievedChunks,
            confidence: response.confidence
        };
        uiManager.showMessage('assistant', response.reply, metadata);
        chatManager.addMessage('assistant', response.reply, metadata);

        uiManager.updateStatus('✓ Ready to chat');
        uiManager.updateTokenInfo(response.tokensUsed);
        uiManager.showToast('Response generated successfully', 'success');

    } catch (error) {
        console.error('Error:', error);
        const errorMsg = `Error: ${error.message}`;
        uiManager.showMessage('assistant', errorMsg);
        chatManager.addMessage('assistant', errorMsg);
        uiManager.showToast(error.message, 'error');
        uiManager.updateStatus('⚠ Error occurred');
    } finally {
        uiManager.showLoading(false);
        uiManager.disableInput(false);
        uiManager.focusInput();
    }
}

async function handleClear() {
    if (confirm('Are you sure you want to clear this conversation?')) {
        try {
            await apiClient.clearSession(chatManager.sessionId);
            chatManager.clearSession();
            uiManager.clearMessages();
            uiManager.showToast('Conversation cleared', 'success');
            uiManager.focusInput();
        } catch (error) {
            uiManager.showToast('Error clearing conversation', 'error');
        }
    }
}

function handleNewChat() {
    if (chatManager.messages.length > 0) {
        if (!confirm('Start a new conversation? Current chat will be saved.')) {
            return;
        }
    }

    chatManager.sessionId = chatManager.generateSessionId();
    localStorage.setItem('sessionId', chatManager.sessionId);
    chatManager.clearSession();
    uiManager.clearMessages();
    uiManager.updateStatus('✓ Ready to chat');
    uiManager.updateTokenInfo('');
    uiManager.showToast('New conversation started', 'success');
    uiManager.focusInput();
}

// ============= GLOBAL FUNCTION FOR SAMPLE BUTTONS =============
function sendMessage(message) {
    const input = document.getElementById('messageInput');
    input.value = message;
    handleSend();
}

// ============= ERROR HANDLING =============
window.addEventListener('error', (e) => {
    console.error('Unhandled error:', e.error);
    if (uiManager) {
        uiManager.showToast('An unexpected error occurred', 'error');
    }
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
    if (uiManager) {
        uiManager.showToast('An unexpected error occurred', 'error');
    }
});
