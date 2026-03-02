from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import mysql.connector
import bcrypt
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="keshavamal123#",
    database="lostfound"
)

# ------------------------
# Utility Functions
# ------------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ------------------------
# Routes
# ------------------------
@app.route('/')
def home():
    return render_template("index.html")

# ------------------------
# Authentication
# ------------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        return jsonify({"message": "Username already exists"}), 400
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                   (username, hashed.decode('utf-8')))
    db.commit()
    return jsonify({"message": "User registered successfully"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401

# ------------------------
# Item Management
# ------------------------
@app.route('/add', methods=['POST'])
def add_item():
    name = request.form['name']
    description = request.form['description']
    image_file = request.files.get('image')
    filename = None
    if image_file and allowed_file(image_file.filename):
        filename = secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    cursor = db.cursor()
    cursor.execute("INSERT INTO items (name, description, image) VALUES (%s, %s, %s)",
                   (name, description, filename))
    db.commit()
    return jsonify({"message": "Item added successfully"})

@app.route('/items', methods=['GET'])
def get_items():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    for item in items:
        if item['image']:
            item['image_url'] = f"/uploads/{item['image']}"
        else:
            item['image_url'] = None
    return jsonify(items)

@app.route('/delete/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM items WHERE id=%s", (item_id,))
    db.commit()
    return jsonify({"message": "Item deleted successfully"})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------------------
# AI/Gemini Call
# ------------------------
@app.route('/ai', methods=['POST'])
def ai_call():
    data = request.json
    question = data.get('question', '')
    # Simple AI simulation
    if 'lost' in question.lower():
        answer = "Please check the Lost Items list above, you might find your item."
    elif 'found' in question.lower():
        answer = "Check the Found Items list, or upload your found item here."
    else:
        answer = "I can help you track lost/found items. Try asking about lost items or found items."
    return jsonify({"answer": answer})

# ------------------------
# Run App
# ------------------------
if __name__ == '__main__':
    app.run(debug=True)