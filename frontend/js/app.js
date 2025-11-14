// ================================
// CONFIGURATION
// ================================
const API_BASE_URL = 'http://localhost:5000/api';

// Global state
let farmerName = '';
let farmLocation = '';

// ================================
// UTILITY FUNCTIONS
// ================================
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

function showNotification(message, type = 'info') {
    alert(message); // Simple notification, can be enhanced with better UI
}

// ================================
// APP INITIALIZATION
// ================================
async function startApp() {
    const nameInput = document.getElementById('farmerName').value.trim();
    const locationInput = document.getElementById('farmLocation').value.trim();
    
    if (!nameInput || !locationInput) {
        showNotification('Please enter your name and location', 'warning');
        return;
    }
    
    farmerName = nameInput;
    farmLocation = locationInput;
    
    showLoading();
    
    try {
        // Get personalized greeting
        const response = await fetch(`${API_BASE_URL}/greeting`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                farmer_name: farmerName,
                farm_location: farmLocation
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('greetingText').textContent = data.greeting;
        }
        
        // Show dashboard
        document.getElementById('welcomeSection').style.display = 'none';
        document.getElementById('dashboardSection').style.display = 'block';
        
    } catch (error) {
        console.error('Error:', error);
        // Still show dashboard even if greeting fails
        document.getElementById('greetingText').textContent = `Hello ${farmerName}!`;
        document.getElementById('welcomeSection').style.display = 'none';
        document.getElementById('dashboardSection').style.display = 'block';
    } finally {
        hideLoading();
    }
}

function logout() {
    document.getElementById('welcomeSection').style.display = 'block';
    document.getElementById('dashboardSection').style.display = 'none';
    hideHealthCheck();
    hideChatbot();
    document.getElementById('farmerName').value = '';
    document.getElementById('farmLocation').value = '';
}

// ================================
// HEALTH CHECK FUNCTIONS
// ================================
function showHealthCheck() {
    document.getElementById('healthCheckForm').style.display = 'block';
    document.getElementById('chatbotSection').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
}

function hideHealthCheck() {
    document.getElementById('healthCheckForm').style.display = 'none';
}

async function checkHealth() {
    const temperature = parseFloat(document.getElementById('temperature').value);
    const milk = parseFloat(document.getElementById('milk').value);
    const respiratory = parseFloat(document.getElementById('respiratory').value);
    const heartRate = parseFloat(document.getElementById('heartRate').value);
    const walking = parseFloat(document.getElementById('walking').value);
    const breed = parseInt(document.getElementById('breed').value);
    const faecal = parseInt(document.getElementById('faecal').value);
    
    // Validation
    if (isNaN(temperature) || isNaN(milk) || isNaN(respiratory) || 
        isNaN(heartRate) || isNaN(walking)) {
        showNotification('Please fill in all fields with valid numbers', 'warning');
        return;
    }
    
    showLoading();
    const checkBtn = document.getElementById('checkBtn');
    checkBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/health-check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                temperature: temperature,
                milk: milk,
                respiratory: respiratory,
                heart_rate: heartRate,
                walking: walking,
                breed: breed,
                faecal: faecal
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            showNotification('Error analyzing health status: ' + data.error, 'error');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showNotification('Failed to connect to server. Please ensure the backend is running.', 'error');
    } finally {
        hideLoading();
        checkBtn.disabled = false;
    }
}

function displayResults(data) {
    const resultsSection = document.getElementById('resultsSection');
    const healthStatus = document.getElementById('healthStatus');
    const confidence = document.getElementById('confidence');
    const recommendations = document.getElementById('recommendations');
    
    // Health status
    healthStatus.textContent = `Health Status: ${data.health_status.toUpperCase()}`;
    healthStatus.className = 'health-status ' + data.health_status.toLowerCase();
    
    // Confidence
    const confidencePercent = (data.confidence * 100).toFixed(1);
    confidence.textContent = `Confidence: ${confidencePercent}%`;
    
    // Recommendations
    recommendations.innerHTML = `
        <h4>🤖 AI Recommendations:</h4>
        <p>${data.recommendations}</p>
    `;
    
    // Show results
    resultsSection.style.display = 'block';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// ================================
// CHATBOT FUNCTIONS
// ================================
function showChatbot() {
    document.getElementById('chatbotSection').style.display = 'block';
    document.getElementById('healthCheckForm').style.display = 'none';
    
    // Add cattle-focused chat suggestions
    displayCattleChatSuggestions();
}

function hideChatbot() {
    document.getElementById('chatbotSection').style.display = 'none';
}

function handleChatEnter(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function validateCattleQuestion(message) {
    const cattleKeywords = [
        'cattle', 'cow', 'cows', 'bull', 'bulls', 'calf', 'calves', 'beef', 'dairy',
        'milk', 'breeding', 'graze', 'pasture', 'feed', 'fodder', 'vaccine', 'disease',
        'health', 'temperature', 'respiratory', 'heart', 'walking', 'faecal', 'manure',
        'udder', 'hoof', 'horn', 'barn', 'shelter', 'water', 'nutrition', 'parasite',
        'worm', 'ticks', 'mastitis', 'foot', 'mouth', 'bloat', 'pneumonia'
    ];
    
    const messageLower = message.toLowerCase();
    const hasCattleKeyword = cattleKeywords.some(keyword => 
        messageLower.includes(keyword)
    );
    
    return hasCattleKeyword;
}

async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    if (!message) {
        return;
    }

    // CATTLE-ONLY VALIDATION
    if (!validateCattleQuestion(message)) {
        addMessageToChat(
            "I specialize only in cattle health and management. Please ask questions about:\n• Cattle diseases and symptoms\n• Milk production and dairy cattle\n• Breeding and calf care\n• Cattle nutrition and feeding\n• Shelter and pasture management\n• Cattle behavior and health monitoring",
            'bot'
        );
        chatInput.value = '';
        return;
    }

    // Add user message to chat
    addMessageToChat(message, 'user');
    chatInput.value = '';

    // Show cattle-specific loading indicator
    const chatMessages = document.getElementById('chatMessages');
    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'message bot-message';
    loadingMsg.id = 'loadingMsg';
    loadingMsg.innerHTML = `
        <div class="message-icon">🐄</div>
        <div class="message-content">
            <p>Analyzing cattle question...</p>
        </div>
    `;
    chatMessages.appendChild(loadingMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                farmer_name: farmerName,
                farm_location: farmLocation
            })
        });

        const data = await response.json();
        loadingMsg.remove();

        if (data.success) {
            addMessageToChat(data.response, 'bot');
        } else {
            addMessageToChat('Sorry, I encountered an error analyzing your cattle question. Please try again.', 'bot');
        }
    } catch (error) {
        console.error('Error:', error);
        loadingMsg.remove();
        addMessageToChat('Failed to connect to cattle health server. Please ensure the backend is running.', 'bot');
    }
}

function addMessageToChat(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const icon = sender === 'user' ? '👨‍🌾' : '🤖';
    
    messageDiv.innerHTML = `
        <div class="message-icon">${icon}</div>
        <div class="message-content">
            <p>${message}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ================================
// INITIALIZE
// ================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🐄 Cattle Health Monitor initialized');
    
    // Add enter key support for welcome form
    document.getElementById('farmerName').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            startApp();
        }
    });
    
    document.getElementById('farmLocation').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            startApp();
        }
    });
});