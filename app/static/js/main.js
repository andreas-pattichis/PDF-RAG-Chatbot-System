// DocuChat Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // File upload handling
    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleFileUpload);
    }

    // Chat form handling
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }

    // Document list loading
    loadDocumentList();
});

/**
 * Handle file upload form submission
 * @param {Event} e - Form submit event
 */
async function handleFileUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('file-input');
    const alertContainer = document.getElementById('alert-container');
    const uploadButton = document.getElementById('upload-button');
    
    // Validate file
    if (!fileInput.files.length) {
        showAlert('Please select a PDF file to upload.', 'error');
        return;
    }
    
    const file = fileInput.files[0];
    if (!file.name.endsWith('.pdf')) {
        showAlert('Only PDF files are supported.', 'error');
        return;
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Show loading state
        uploadButton.disabled = true;
        uploadButton.innerHTML = '<div class="spinner"></div> Uploading...';
        
        // Upload file
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Error uploading file');
        }
        
        // Show success message
        showAlert(data.message, 'success');
        
        // Reset form
        fileInput.value = '';
        
        // Reload document list
        loadDocumentList();
        
    } catch (error) {
        showAlert(error.message, 'error');
    } finally {
        // Reset button state
        uploadButton.disabled = false;
        uploadButton.innerHTML = 'Upload PDF';
    }
}

/**
 * Handle chat form submission
 * @param {Event} e - Form submit event
 */
async function handleChatSubmit(e) {
    e.preventDefault();
    
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    
    // Clear input
    messageInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Send message to API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Error generating response');
        }
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Add bot response to chat
        addMessageToChat(data.response, 'bot', data.sources);
        
    } catch (error) {
        hideTypingIndicator();
        addMessageToChat('Sorry, I encountered an error: ' + error.message, 'bot');
    }
    
    // Scroll to bottom of chat
    scrollChatToBottom();
}

/**
 * Add a message to the chat container
 * @param {string} content - Message content
 * @param {string} sender - Message sender ('user' or 'bot')
 * @param {Array} sources - Optional sources for bot messages
 */
function addMessageToChat(content, sender, sources = []) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.className = `message message-${sender}`;
    
    // Format message content
    let formattedContent = content.replace(/\n/g, '<br>');
    
    // Create message HTML
    messageElement.innerHTML = `
        <div class="message-content">${formattedContent}</div>
        <div class="message-meta">
            <span>${sender === 'user' ? 'You' : 'DocuChat'}</span>
            <span>${new Date().toLocaleTimeString()}</span>
        </div>
    `;
    
    // Add sources for bot messages
    if (sender === 'bot' && sources && sources.length > 0) {
        const sourcesContainer = document.createElement('div');
        sourcesContainer.className = 'source-citations';
        
        const sourcesList = sources.map(source => {
            return `<span class="source-item">${source.document}${source.page ? ` (p. ${source.page})` : ''}</span>`;
        }).join('');
        
        sourcesContainer.innerHTML = `
            <div>Sources:</div>
            ${sourcesList}
        `;
        
        messageElement.appendChild(sourcesContainer);
    }
    
    chatMessages.appendChild(messageElement);
    scrollChatToBottom();
}

/**
 * Show typing indicator in chat
 */
function showTypingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.id = 'typing-indicator';
    typingIndicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    chatMessages.appendChild(typingIndicator);
    scrollChatToBottom();
}

/**
 * Hide typing indicator
 */
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

/**
 * Scroll chat container to bottom
 */
function scrollChatToBottom() {
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Load document list from API
 */
async function loadDocumentList() {
    const documentList = document.getElementById('document-list');
    if (!documentList) return;
    
    try {
        // Show loading state
        documentList.innerHTML = '<div class="text-center p-4"><div class="spinner mx-auto"></div><div class="mt-2">Loading documents...</div></div>';
        
        // Fetch documents
        const response = await fetch('/api/documents');
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Error loading documents');
        }
        
        // Display documents
        if (data.documents && data.documents.length > 0) {
            const documentsHTML = data.documents.map(doc => {
                const uploadDate = new Date(doc.upload_date).toLocaleDateString();
                return `
                    <li class="document-item">
                        <div class="document-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                <polyline points="14 2 14 8 20 8"></polyline>
                                <path d="M9 15v-6"></path>
                                <path d="M12 15v-6"></path>
                                <path d="M15 15v-6"></path>
                            </svg>
                        </div>
                        <div class="document-info">
                            <div class="document-title">${doc.filename}</div>
                            <div class="document-meta">Uploaded on ${uploadDate}</div>
                        </div>
                        <div class="document-actions">
                            <button class="btn btn-secondary btn-sm" onclick="chatWithDocument('${doc.document_id}')">
                                Chat
                            </button>
                        </div>
                    </li>
                `;
            }).join('');
            
            documentList.innerHTML = documentsHTML;
        } else {
            documentList.innerHTML = '<div class="text-center p-4">No documents uploaded yet.</div>';
        }
        
    } catch (error) {
        documentList.innerHTML = `<div class="text-center p-4 text-red-500">Error: ${error.message}</div>`;
    }
}

/**
 * Show an alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type ('success', 'error', 'warning')
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type}`;
    alertElement.innerHTML = message;
    
    // Clear existing alerts
    alertContainer.innerHTML = '';
    
    // Add new alert
    alertContainer.appendChild(alertElement);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        alertElement.remove();
    }, 5000);
}

/**
 * Navigate to chat page for a specific document
 * @param {string} documentId - Document ID
 */
function chatWithDocument(documentId) {
    window.location.href = `/chat?document=${documentId}`;
}

/**
 * Auto-resize textarea based on content
 * @param {HTMLElement} element - Textarea element
 */
function autoResizeTextarea(element) {
    element.style.height = 'auto';
    element.style.height = (element.scrollHeight) + 'px';
}