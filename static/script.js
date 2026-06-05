/* ================================================
   LOST & FOUND - PREMIUM JAVASCRIPT
   Advanced Animations, Interactions & API Integration
   ================================================ */

// ===== TOAST NOTIFICATIONS =====
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 300ms ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ===== PASSWORD STRENGTH INDICATOR =====
document.getElementById('regPassword')?.addEventListener('input', (e) => {
    const strength = calculatePasswordStrength(e.target.value);
    const bars = document.querySelectorAll('#regStrength .strength-bar');
    bars.forEach((bar, idx) => {
        bar.className = 'strength-bar';
        if (idx < strength) {
            bar.classList.add(strength === 1 ? 'weak' : strength === 2 ? 'medium' : 'strong');
        }
    });
});

function calculatePasswordStrength(password) {
    if (password.length < 6) return 1;
    if (password.length < 10) return 2;
    return 3;
}

// ===== FILE UPLOAD HANDLERS =====
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('itemImage');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');

uploadArea?.addEventListener('click', () => fileInput.click());

uploadArea?.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('active');
});

uploadArea?.addEventListener('dragleave', () => {
    uploadArea.classList.remove('active');
});

uploadArea?.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('active');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        previewImage();
    }
});

fileInput?.addEventListener('change', previewImage);

function previewImage() {
    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImg.src = e.target.result;
            imagePreview.style.display = 'block';
        };
        reader.readAsDataURL(fileInput.files[0]);
    }
}

// ===== FORM SUBMISSION HANDLERS =====
document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;
    const confirm = document.getElementById('regConfirm').value;
    
    if (password !== confirm) {
        showToast('Passwords do not match!', 'error');
        return;
    }
    
    if (password.length < 6) {
        showToast('Password must be at least 6 characters', 'error');
        return;
    }
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            showToast('Account created successfully!', 'success');
            document.getElementById('registerForm').reset();
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Registration failed. Username may already exist.', 'error');
        }
    } catch (error) {
        showToast('Network error', 'error');
    }
});

document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('logUsername').value;
    const password = document.getElementById('logPassword').value;
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            showToast('Logged in successfully!', 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showToast('Invalid credentials', 'error');
        }
    } catch (error) {
        showToast('Network error', 'error');
    }
});

document.getElementById('itemForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('name', document.getElementById('itemName').value);
    formData.append('description', document.getElementById('itemDescription').value);
    formData.append('category', document.getElementById('itemCategory').value);
    formData.append('status', document.querySelector('input[name="status"]:checked').value);
    
    if (fileInput.files && fileInput.files[0]) {
        formData.append('image', fileInput.files[0]);
    }
    
    try {
        const response = await fetch('/add', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            showToast('Item reported successfully!', 'success');
            document.getElementById('itemForm').reset();
            imagePreview.style.display = 'none';
            loadItems();
        } else {
            showToast('Failed to add item', 'error');
        }
    } catch (error) {
        showToast('Network error', 'error');
    }
});

// ===== ITEM MANAGEMENT =====
async function loadItems() {
    try {
        const response = await fetch('/items');
        const items = await response.json();
        displayItems(items);
        updateStats(items);
    } catch (error) {
        console.error('Error loading items:', error);
    }
}

function displayItems(items) {
    const grid = document.getElementById('itemsGrid');
    
    if (items.length === 0) {
        grid.innerHTML = `
            <div class="item-card glass-card" style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                <p style="color: var(--text-tertiary); font-size: 1.125rem;">No items yet. Be the first to report an item!</p>
            </div>
        `;
        return;
    }
    
    grid.innerHTML = items.map(item => `
        <div class="item-card glass-card">
            <div class="item-image">
                ${item.image ? `<img src="/uploads/${item.image}" alt="${item.name}">` : '<div style="font-size: 3rem;">📦</div>'}
            </div>
            <div class="item-content">
                <div class="item-name">${item.name}</div>
                <p class="item-description">${item.description}</p>
                <div class="item-meta">
                    <span class="badge ${item.status}">${item.status.toUpperCase()}</span>
                    <span class="badge">${item.category || 'Uncategorized'}</span>
                </div>
                <div class="item-date">Added ${new Date(item.date_added).toLocaleDateString()}</div>
                <div class="item-actions">
                    <button class="btn-delete" onclick="deleteItem(${item.id})">Delete</button>
                </div>
            </div>
        </div>
    `).join('');
}

async function deleteItem(id) {
    if (!confirm('Delete this item?')) return;
    
    try {
        const response = await fetch(`/delete/${id}`, { method: 'POST' });
        if (response.ok) {
            showToast('Item deleted', 'success');
            loadItems();
        }
    } catch (error) {
        showToast('Error deleting item', 'error');
    }
}

// ===== STATISTICS =====
function updateStats(items) {
    const total = items.length;
    const lost = items.filter(i => i.status === 'lost').length;
    const found = items.filter(i => i.status === 'found').length;
    const matched = 0; // Placeholder
    
    document.getElementById('statTotal').textContent = animateNumber(total);
    document.getElementById('statLost').textContent = animateNumber(lost);
    document.getElementById('statFound').textContent = animateNumber(found);
    document.getElementById('statMatched').textContent = animateNumber(matched);
}

function animateNumber(target) {
    return target;
}

// ===== AI CHATBOT =====
function toggleChat() {
    const chatWindow = document.getElementById('chatWindow');
    chatWindow.classList.toggle('active');
    if (chatWindow.classList.contains('active')) {
        document.getElementById('chatInput').focus();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    const messagesDiv = document.getElementById('chatMessages');
    
    // Add user message
    const userBubble = document.createElement('div');
    userBubble.className = 'message user';
    userBubble.innerHTML = `<div class="message-bubble">${escapeHtml(message)}</div>`;
    messagesDiv.appendChild(userBubble);
    
    input.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    try {
        const response = await fetch('/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        const aiBubble = document.createElement('div');
        aiBubble.className = 'message ai';
        aiBubble.innerHTML = `<div class="message-bubble">${escapeHtml(data.response || 'I encountered an error. Please try again.')}</div>`;
        messagesDiv.appendChild(aiBubble);
        
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch (error) {
        const errorBubble = document.createElement('div');
        errorBubble.className = 'message ai';
        errorBubble.innerHTML = `<div class="message-bubble">Sorry, I couldn't connect. Please try again.</div>`;
        messagesDiv.appendChild(errorBubble);
    }
}

function handleChatKeypress(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        sendMessage();
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ===== SCROLL REVEAL ANIMATIONS =====
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeIn 600ms ease-out forwards';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
    loadItems();
    
    // Observe elements for scroll reveal
    document.querySelectorAll('.item-card, .stat-card, .auth-card, .form-card').forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
    
    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const element = document.querySelector(href);
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
});
