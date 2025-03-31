// script.js

// State management
let sessionId = null;
let isUploading = false;

// DOM Elements
const uploadSection = document.getElementById('uploadSection');
const chatSection = document.getElementById('chatSection');
const uploadBtn = document.getElementById('uploadBtn');
const sendBtn = document.getElementById('sendBtn');
const chatInput = document.getElementById('chatInput');
const pdfInput = document.getElementById('pdfInput');
const uploadStatus = document.getElementById('uploadStatus');
const chatWindow = document.getElementById('chatWindow');
const toggleUploadBtn = document.getElementById('toggleUpload');
const dropzone = document.getElementById('dropzone');
const noMessages = document.getElementById('noMessages');
const sessionInfo = document.getElementById('sessionInfo');

// Initialize the app
function init() {
    // Event listeners
    uploadBtn.onclick = function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (!pdfInput.files.length) {
            updateUploadStatus('Please select a PDF file.', 'error');
            return;
        }
        handleUpload();
    };
    
    sendBtn.addEventListener('click', handleSendMessage);
    pdfInput.addEventListener('change', handleFileSelected);
    chatInput.addEventListener('keydown', handleEnterKey);
    toggleUploadBtn.addEventListener('click', toggleUploadSection);
    
    // Drag and drop functionality
    setupDragAndDrop();
}

// Setup drag and drop functionality
function setupDragAndDrop() {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropzone.addEventListener('drop', handleDrop, false);
    
    // Add click handler to dropzone (not using label anymore)
    dropzone.addEventListener('click', function(e) {
        // If they click on the input itself, don't do anything special
        if (e.target === pdfInput) return;
        
        // Otherwise, trigger the file input
        e.preventDefault();
        e.stopPropagation();
        pdfInput.click();
    });
}

// Helper functions for drag and drop
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight() {
    dropzone.classList.add('dragover');
}

function unhighlight() {
    dropzone.classList.remove('dragover');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length && files[0].type === 'application/pdf') {
        pdfInput.files = files;
        handleFileSelected();
    } else {
        updateUploadStatus('Please select a PDF file.', 'error');
    }
}

// Handle file selection
function handleFileSelected() {
    const file = pdfInput.files[0];
    
    if (file) {
        uploadBtn.disabled = false;
        updateUploadStatus(`File selected: ${file.name}`, 'normal');
        
        // Make the dropzone look like it has a file
        dropzone.classList.add('has-file');
        const fileName = document.createElement('div');
        fileName.className = 'selected-file';
        fileName.textContent = file.name;
        
        // Clear any existing file name display
        const existingFileName = dropzone.querySelector('.selected-file');
        if (existingFileName) {
            existingFileName.remove();
        }
        
        dropzone.appendChild(fileName);
    } else {
        uploadBtn.disabled = true;
        updateUploadStatus('', 'normal');
    }
}

// Toggle upload section expanded/minimized
function toggleUploadSection() {
    const isMinimized = uploadSection.classList.toggle('minimized');
    
    // Change the toggle button icon
    if (isMinimized) {
        toggleUploadBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
        `;
    } else {
        toggleUploadBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
                <polyline points="18 15 12 9 6 15"></polyline>
            </svg>
        `;
    }
}

// Handle upload button click
async function handleUpload() {
    const fileInput = document.getElementById('pdfInput');
    
    if (isUploading) return;
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);

    // Show loading state
    isUploading = true;
    uploadBtn.disabled = true;
    updateUploadStatus('Uploading...', 'loading');

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        
        if (response.ok) {
            sessionId = data.session_id;
            updateUploadStatus('Upload successful!', 'success');
            
            // Minimize the upload section
            uploadSection.classList.add('minimized');
            toggleUploadBtn.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            `;
            
            // Show and activate chat section with animation
            setTimeout(() => {
                chatSection.classList.add('active');
                chatInput.disabled = false;
                sendBtn.disabled = false;
                chatInput.focus();
                
                // Update session info
                sessionInfo.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    ${file.name.substring(0, 20)}${file.name.length > 20 ? '...' : ''}
                `;
            }, 300);
        } else {
            updateUploadStatus(`Error: ${data.detail}`, 'error');
            uploadBtn.disabled = false;
        }
    } catch (error) {
        updateUploadStatus(`Error: ${error.message}`, 'error');
        uploadBtn.disabled = false;
    } finally {
        isUploading = false;
    }
}

// Update upload status with appropriate styling
function updateUploadStatus(message, type = 'normal') {
    uploadStatus.textContent = '';
    uploadStatus.className = 'upload-status';
    
    if (type === 'loading') {
        uploadStatus.className += ' status-loading';
        const spinner = document.createElement('div');
        spinner.className = 'spinner';
        uploadStatus.appendChild(spinner);
        uploadStatus.appendChild(document.createTextNode(' ' + message));
    } else {
        uploadStatus.textContent = message;
        if (type === 'error') uploadStatus.className += ' status-error';
        if (type === 'success') uploadStatus.className += ' status-success';
    }
}

// Handle Enter key in chat input
function handleEnterKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
}

// Handle send message button click
async function handleSendMessage() {
    const message = chatInput.value.trim();
    if (!message || !sessionId) return;
    
    // Clear input and disable button
    chatInput.value = '';
    sendBtn.disabled = true;
    chatInput.disabled = true;
    
    // Hide "no messages" placeholder if it's showing
    if (noMessages.style.display !== 'none') {
        noMessages.style.display = 'none';
    }
    
    // Add user message to chat
    appendMessage('user', message);
    
    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ session_id: sessionId, question: message })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        hideTypingIndicator();
        
        if (response.ok) {
            appendMessage('bot', data.answer);
        } else {
            appendMessage('bot', `Error: ${data.detail}`);
        }
    } catch (error) {
        hideTypingIndicator();
        appendMessage('bot', `Error: ${error.message}`);
    } finally {
        // Re-enable input and button
        chatInput.disabled = false;
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

// Show typing indicator
function showTypingIndicator() {
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.id = 'typingIndicator';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'typing-dot';
        typingIndicator.appendChild(dot);
    }
    
    chatWindow.appendChild(typingIndicator);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Append message to chat window
function appendMessage(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    
    // Format the message properly if it contains numbered points
    if (sender === 'bot' && (message.match(/\d+\.\s/g) || []).length > 1) {
        // This is likely a list of points, so let's format it nicely
        const formattedContent = document.createElement('div');
        formattedContent.className = 'formatted-content';
        
        // Split by numbered points (1., 2., etc.)
        const parts = message.split(/(\d+\.\s)/g);
        
        if (parts.length > 1) {
            let currentPoint = document.createElement('div');
            currentPoint.className = 'point-item';
            
            for (let i = 0; i < parts.length; i++) {
                // If this part is a point number
                if (parts[i].match(/^\d+\.\s$/)) {
                    // If we already have content, add the current point to the formatted content
                    if (currentPoint.textContent.trim()) {
                        formattedContent.appendChild(currentPoint);
                        currentPoint = document.createElement('div');
                        currentPoint.className = 'point-item';
                    }
                    
                    // Create a strong element for the point number
                    const pointNumber = document.createElement('strong');
                    pointNumber.textContent = parts[i];
                    currentPoint.appendChild(pointNumber);
                } else if (parts[i].trim()) {
                    // Add the content of the point
                    currentPoint.appendChild(document.createTextNode(parts[i]));
                }
            }
            
            // Add the last point if it exists
            if (currentPoint.textContent.trim()) {
                formattedContent.appendChild(currentPoint);
            }
            
            messageDiv.appendChild(formattedContent);
        } else {
            // Fallback to regular text if the splitting didn't work
            messageDiv.textContent = message;
        }
    } else {
        // Just regular text, no special formatting
        messageDiv.textContent = message;
    }
    
    // Add timestamp
    const timestamp = document.createElement('div');
    timestamp.className = 'message-time';
    timestamp.textContent = getCurrentTime();
    messageDiv.appendChild(timestamp);
    
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Get current time formatted as HH:MM
function getCurrentTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', init);