from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import mysql.connector
import bcrypt
import os
import json
from werkzeug.utils import secure_filename
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# ------------------------
# Gemini Setup
# ------------------------

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ------------------------
# Upload folder
# ------------------------

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png','jpg','jpeg','gif'}

# ------------------------
# Database connection
# ------------------------
from flask import g

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="keshavamal123#",
            database="lostfound"
        )
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

class DBProxy:
    def cursor(self, *args, **kwargs):
        return get_db().cursor(*args, **kwargs)
    def commit(self, *args, **kwargs):
        return get_db().commit(*args, **kwargs)

db = DBProxy()

# ------------------------
# Utility
# ------------------------

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------------
# Home
# ------------------------

@app.route('/')
def home():
    return render_template("index.html")


# ------------------------
# Register
# ------------------------

@app.route('/register', methods=['POST'])
def register():

    data = request.json
    username = data['username']
    password = data['password']

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s",(username,))

    if cursor.fetchone():
        return jsonify({"message":"Username already exists"}),400

    cursor.execute(
        "INSERT INTO users (username,password) VALUES (%s,%s)",
        (username,hashed.decode('utf-8'))
    )

    db.commit()

    return jsonify({"message":"User registered successfully"})


# ------------------------
# Login
# ------------------------

@app.route('/login', methods=['POST'])
def login():

    data=request.json
    username=data['username']
    password=data['password']

    cursor=db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s",(username,))
    user=cursor.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return jsonify({"message":"Login successful"})

    return jsonify({"message":"Invalid credentials"}),401


# ------------------------
# Add Item
# ------------------------

@app.route('/add', methods=['POST'])
def add_item():

    name=request.form['name']
    description=request.form['description']
    item_type=request.form.get('type', 'lost')
    category=request.form.get('category', 'Other')
    lat=request.form.get('lat')
    lng=request.form.get('lng')
    
    lat = float(lat) if lat else None
    lng = float(lng) if lng else None

    image_file=request.files.get('image')
    filename=None

    if image_file and allowed_file(image_file.filename):

        filename=secure_filename(image_file.filename)
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    db = get_db()
    cursor=db.cursor()

    cursor.execute(
        "INSERT INTO items (name,description,image,type,status,lat,lng,category) VALUES (%s,%s,%s,%s,'open',%s,%s,%s)",
        (name,description,filename,item_type,lat,lng,category)
    )

    db.commit()

    return jsonify({"message":"Item added successfully"})


# ------------------------
# Get Items
# ------------------------

@app.route('/items', methods=['GET'])
def get_items():

    cursor=db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM items ORDER BY id DESC")
    items=cursor.fetchall()

    for item in items:
        if 'created_at' in item and item['created_at']:
            item['date'] = item['created_at'].strftime('%b %d, %Y')
        else:
            item['date'] = 'Today'
            
        if item['image']:
            item['image_url']=f"/uploads/{item['image']}"
        else:
            item['image_url']=None

    return jsonify(items)


# ------------------------
# Admin Dashboard Metrics
# ------------------------

@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    image_file = request.files.get('image')
    item_type = request.form.get('type', 'lost')
    user_lat = request.form.get('lat')
    user_lng = request.form.get('lng')
    
    if not image_file:
        return jsonify({"error": "No image provided"}), 400
        
    try:
        from PIL import Image
        img = Image.open(image_file.stream)
        
        opposite_type = 'found' if item_type == 'lost' else 'lost'
        
        cursor=db.cursor(dictionary=True)
        
        if user_lat and user_lng:
            query = """
            SELECT id, name, description, 
                   ( 6371 * acos( cos( radians(%s) ) * cos( radians( lat ) ) * cos( radians( lng ) - radians(%s) ) + sin( radians(%s) ) * sin( radians( lat ) ) ) ) AS distance_km
            FROM items WHERE type=%s AND status='open' AND lat IS NOT NULL
            ORDER BY distance_km ASC LIMIT 15
            """
            cursor.execute(query, (user_lat, user_lng, user_lat, opposite_type))
        else:
            cursor.execute("SELECT id, name, description FROM items WHERE type=%s AND status='open' LIMIT 15", (opposite_type,))
            
        opposite_items = cursor.fetchall()
        
        for item in opposite_items:
            if 'distance_km' in item and item['distance_km'] is not None:
                item['distance_km'] = round(item['distance_km'], 2)
        
        prompt = (
            f"You are an AI for a Lost & Found system. The user uploaded an image of a {item_type} item.\n"
            '1. Identify what the item is and write a short name to auto-fill a form starting with "Looks like a ". '
            'Keep it concise (e.g. "Looks like a black wallet").\n'
            '2. Write a brief description of the item based on the image.\n'
            f"3. Here is a JSON list of currently open '{opposite_type}' items (includes physical distance in km if pinned): {json.dumps(opposite_items)}\n"
            "   Return a list of IDs of ANY items from this JSON that could be a match. Prioritize items closer in distance!\n"
            "Reply strictly with ONLY a valid JSON string (no markdown formatting, no ``` code blocks) matching this exact format: "
            '{"detected_name": "...", "detected_description": "...", "matched_ids": []}'
        )
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([prompt, img])
        
        # clean response text from markdown block just in case
        text = response.text.replace('```json', '').replace('```', '').strip()
        data = json.loads(text)
        
        return jsonify(data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    cursor=db.cursor(dictionary=True)
    
    # Total lost items
    cursor.execute("SELECT COUNT(*) as count FROM items WHERE type='lost'")
    total_lost = cursor.fetchone()['count']
    
    # Found items
    cursor.execute("SELECT COUNT(*) as count FROM items WHERE type='found'")
    total_found = cursor.fetchone()['count']
    
    # Success rate
    cursor.execute("SELECT COUNT(*) as count FROM items WHERE type='lost' AND status='resolved'")
    resolved_lost = cursor.fetchone()['count']
    
    success_rate = 0
    if total_lost > 0:
        success_rate = round((resolved_lost / total_lost) * 100, 1)
        
    # Most common lost items
    cursor.execute("SELECT name, COUNT(*) as count FROM items WHERE type='lost' GROUP BY name ORDER BY count DESC LIMIT 5")
    common_items = [row['name'] for row in cursor.fetchall()]
    
    return jsonify({
        "total_lost": total_lost,
        "total_found": total_found,
        "success_rate": success_rate,
        "common_items": common_items
    })


# ------------------------
# Resolve Item
# ------------------------

@app.route('/resolve/<int:item_id>', methods=['POST'])
def resolve_item(item_id):
    cursor=db.cursor()
    cursor.execute("UPDATE items SET status='resolved' WHERE id=%s",(item_id,))
    db.commit()
    return jsonify({"message":"Item marked as resolved"})


# ------------------------
# Delete Item
# ------------------------

@app.route('/delete/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):

    cursor=db.cursor()
    cursor.execute("DELETE FROM items WHERE id=%s",(item_id,))
    db.commit()

    return jsonify({"message":"Item deleted successfully"})


# ------------------------
# Upload Images
# ------------------------

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ------------------------
# AI Chatbot
# ------------------------

@app.route('/ai', methods=['POST'])
def ai_call():

    data=request.json
    question=data.get('question','')
    chat_history=data.get('history', [])

    try:
        cursor=db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM items")
        items=cursor.fetchall()
        
        items_context = "Current items in our lost and found database:\n"
        for item in items:
            items_context += f"- ID: {item.get('id', 'N/A')}, Name: {item['name']}, Description: {item['description']}\n"

        system_prompt = (
            "You are a helpful AI assistant for a Lost & Found website. "
            "Use the following database items to answer the user's queries. "
            "If an item matches their query, let them know. If not, tell them it hasn't been found yet.\n\n"
            f"{items_context}"
        )

        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
        
        gemini_history = []
        for msg in chat_history:
            role = 'user' if msg['role'] == 'user' else 'model'
            gemini_history.append({"role": role, "parts": [msg['content']]})

        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(question)

        return jsonify({"answer": response.text})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"answer":f"AI service unavailable. Details: {str(e)}"})


# ------------------------
# Run
# ------------------------

if __name__ == '__main__':
    app.run(debug=True)