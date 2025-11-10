// View Management
const navItems = document.querySelectorAll('.nav-item');
const views = document.querySelectorAll('.view');

navItems.forEach(item => {
    item.addEventListener('click', () => {
        const viewName = item.dataset.view;
        
        navItems.forEach(nav => nav.classList.remove('active'));
        views.forEach(view => view.classList.remove('active'));
        
        item.classList.add('active');
        document.getElementById(`${viewName}-view`).classList.add('active');
    });
});

// Chat Functionality
const messageInput = document.getElementById('message-input');
const sendBtn = document.getElementById('send-btn');
const messagesContainer = document.getElementById('messages');

let authToken = localStorage.getItem('otis_token');

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    messageInput.value = '';

    try {
        const response = await window.api.request('/api/v1/agent/run', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                instruction: message,
                mode: 'passive',
                max_iterations: 5
            })
        });

        addMessage(response.result || 'Task completed', 'assistant');
    } catch (error) {
        addMessage('Error: ' + error.message, 'error');
    }
}

function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.style.cssText = `
        padding: 16px;
        margin-bottom: 12px;
        border-radius: 12px;
        background: ${type === 'user' ? 'rgba(118, 185, 0, 0.1)' : 'rgba(139, 92, 246, 0.1)'};
        border: 1px solid ${type === 'user' ? 'rgba(118, 185, 0, 0.2)' : 'rgba(139, 92, 246, 0.2)'};
        animation: slideIn 0.3s ease-out;
    `;
    messageDiv.textContent = text;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Quick Actions
document.querySelectorAll('.action-card').forEach(card => {
    card.addEventListener('click', async () => {
        const action = card.dataset.action;
        const actions = {
            scan: 'Perform a port scan on scanme.nmap.org',
            vuln: 'Check for common vulnerabilities',
            report: 'Generate a security assessment report'
        };
        
        messageInput.value = actions[action];
        sendMessage();
    });
});

// Auto-login or show login prompt
async function checkAuth() {
    if (!authToken) {
        const username = prompt('Username:');
        const password = prompt('Password:');
        
        try {
            const response = await window.api.request('/api/v1/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
            
            authToken = response.access_token;
            localStorage.setItem('otis_token', authToken);
            addMessage('Connected to Otis', 'assistant');
        } catch (error) {
            addMessage('Authentication failed. Please restart.', 'error');
        }
    } else {
        addMessage('Welcome back! How can I help with security today?', 'assistant');
    }
}

checkAuth();

// Load scans on view switch
document.querySelector('[data-view="scans"]').addEventListener('click', loadScans);

async function loadScans() {
    const scanGrid = document.getElementById('scan-grid');
    scanGrid.innerHTML = '<p style="color: var(--text-tertiary);">Loading scans...</p>';
    
    try {
        const response = await window.api.request('/api/v1/scans', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        scanGrid.innerHTML = response.scans?.map(scan => `
            <div class="action-card">
                <div class="action-text">
                    <div class="action-title">${scan.target}</div>
                    <div class="action-desc">${scan.status} - ${new Date(scan.created_at).toLocaleString()}</div>
                </div>
            </div>
        `).join('') || '<p>No scans found</p>';
    } catch (error) {
        scanGrid.innerHTML = '<p style="color: #ff3b30;">Failed to load scans</p>';
    }
}
