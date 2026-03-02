// Load items
function loadItems() {
    fetch("/items")
    .then(res => res.json())
    .then(data => {
        const itemsList = document.getElementById("items");
        itemsList.innerHTML = "";
        data.forEach(item => {
            const li = document.createElement("li");
            li.innerHTML = `
                <strong>${item.name}</strong> - ${item.description}<br>
                ${item.image_url ? `<img src="${item.image_url}" width="150">` : ""}
            `;
            itemsList.appendChild(li);
        });
    });
}

// Add item form
document.getElementById('addForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', document.getElementById('name').value);
    formData.append('description', document.getElementById('description').value);
    const imageFile = document.getElementById('image').files[0];
    if(imageFile) formData.append('image', imageFile);

    fetch('/add', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => { alert(data.message); loadItems(); document.getElementById('addForm').reset(); });
});

// Register
function register() {
    fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: document.getElementById('reg_username').value,
            password: document.getElementById('reg_password').value
        })
    }).then(res => res.json())
      .then(data => alert(data.message));
}

// Login
function login() {
    fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: document.getElementById('login_username').value,
            password: document.getElementById('login_password').value
        })
    }).then(res => res.json())
      .then(data => alert(data.message));
}

// AI/Gemini call
function askAI() {
    const question = document.getElementById('ai_input').value;
    if (!question) return;

    fetch('/ai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById('ai_response').innerText = data.answer;
        document.getElementById('ai_input').value = '';
    });
}

loadItems();