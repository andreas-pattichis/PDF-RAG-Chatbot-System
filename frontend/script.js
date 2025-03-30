// script.js

let sessionId = null;

document.getElementById("uploadBtn").addEventListener("click", async () => {
    const fileInput = document.getElementById("pdfInput");
    const uploadStatus = document.getElementById("uploadStatus");
    if (!fileInput.files.length) {
        uploadStatus.textContent = "Please select a PDF file.";
        return;
    }
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    uploadStatus.textContent = "Uploading...";
    try {
        const response = await fetch("/api/upload", {
            method: "POST",
            body: formData,
        });
        const data = await response.json();
        if (response.ok) {
            sessionId = data.session_id;
            uploadStatus.textContent = "Upload successful! Session ID: " + sessionId;
            document.querySelector(".chat-section").style.display = "block";
        } else {
            uploadStatus.textContent = "Error: " + data.detail;
        }
    } catch (error) {
        uploadStatus.textContent = "Error: " + error;
    }
});

document.getElementById("sendBtn").addEventListener("click", async () => {
    const chatInput = document.getElementById("chatInput");
    const message = chatInput.value.trim();
    if (!message || !sessionId) return;
    
    appendMessage("user", message);
    chatInput.value = "";

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ session_id: sessionId, question: message })
        });
        const data = await response.json();
        if (response.ok) {
            appendMessage("bot", data.answer);
        } else {
            appendMessage("bot", "Error: " + data.detail);
        }
    } catch (error) {
        appendMessage("bot", "Error: " + error);
    }
});

function appendMessage(sender, message) {
    const chatWindow = document.getElementById("chatWindow");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    messageDiv.textContent = message;
    chatWindow.appendChild(messageDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}
