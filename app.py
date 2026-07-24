# app.py
from flask import Flask, render_template, jsonify, request, session
from werkzeug.security import check_password_hash
import sqlite3
import os

app = Flask(__name__)
# This key secures your session cookies. In a real deployment, keep this in a .env file!
app.secret_key = 'super_secret_development_key' 

# Auto-initialize database if it does not exist (useful for clean Render deployments)
if not os.path.exists('portfolio.db'):
    import sys
    import subprocess
    print("portfolio.db not found. Initializing database...", flush=True)
    try:
        subprocess.run([sys.executable, "init_db.py"], check=True)
    except Exception as e:
        print(f"Error running database initialization: {e}", flush=True)

def get_db_connection():
    conn = sqlite3.connect('portfolio.db')
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/projects')
def get_projects():
    conn = get_db_connection()
    projects = conn.execute('SELECT * FROM projects').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in projects])

# --- NEW AUTHENTICATION ROUTES ---

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    # Check if user exists and the password matches the hash
    if user and check_password_hash(user['password_hash'], password):
        session['role'] = 'admin'  # Store role in the browser's session cookie
        return jsonify({"status": "success", "role": "admin"})
    
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('role', None) # Remove the session data
    return jsonify({"status": "success"})

@app.route('/api/auth_status')
def auth_status():
    role = session.get('role', 'guest')
    return jsonify({"role": role})

# --- ADMIN CRUD ROUTES FOR PROJECTS ---

@app.route('/api/projects', methods=['POST'])
def add_project():
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO projects (title, description, tech_stack, image_url, github_url, live_url, featured, system_diagram_url, star_situation, star_task, star_action, star_result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['title'], data['description'], data['tech_stack'], 
          data.get('image_url', ''), data.get('github_url', ''), 
          data.get('live_url', ''), data.get('featured', 0),
          data.get('system_diagram_url', ''), data.get('star_situation', ''),
          data.get('star_task', ''), data.get('star_action', ''),
          data.get('star_result', '')))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"status": "success", "id": new_id})

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
        
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        UPDATE projects 
        SET title = ?, description = ?, tech_stack = ?, image_url = ?, github_url = ?, live_url = ?, featured = ?, system_diagram_url = ?, star_situation = ?, star_task = ?, star_action = ?, star_result = ?
        WHERE id = ?
    ''', (data['title'], data['description'], data['tech_stack'], 
          data.get('image_url', ''), data.get('github_url', ''), 
          data.get('live_url', ''), data.get('featured', 0),
          data.get('system_diagram_url', ''), data.get('star_situation', ''),
          data.get('star_task', ''), data.get('star_action', ''),
          data.get('star_result', ''), project_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
        
    conn = get_db_connection()
    conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# --- PROFILE ENDPOINTS ---

@app.route('/api/profile', methods=['GET'])
def get_profile():
    conn = get_db_connection()
    profile = conn.execute('SELECT * FROM profile ORDER BY id ASC LIMIT 1').fetchone()
    conn.close()
    if profile:
        return jsonify(dict(profile))
    return jsonify({"error": "Profile not found"}), 404

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        UPDATE profile
        SET name = ?, title = ?, bio = ?, profile_picture = ?, github_link = ?, linkedin_link = ?, email = ?, resume_url = ?
        WHERE id = 1
    ''', (data['name'], data['title'], data['bio'], data.get('profile_picture', ''), 
          data.get('github_link', ''), data.get('linkedin_link', ''), 
          data.get('email', ''), data.get('resume_url', '')))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# --- SKILLS ENDPOINTS ---

@app.route('/api/skills', methods=['GET'])
def get_skills():
    conn = get_db_connection()
    skills = conn.execute('SELECT * FROM skills ORDER BY category, name').fetchall()
    conn.close()
    return jsonify([dict(s) for s in skills])

@app.route('/api/skills', methods=['POST'])
def add_skill():
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO skills (name, category, proficiency) VALUES (?, ?, ?)
    ''', (data['name'], data['category'], data.get('proficiency', 80)))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"status": "success", "id": new_id})

@app.route('/api/skills/<int:skill_id>', methods=['PUT'])
def update_skill(skill_id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        UPDATE skills SET name = ?, category = ?, proficiency = ? WHERE id = ?
    ''', (data['name'], data['category'], data.get('proficiency', 80), skill_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/skills/<int:skill_id>', methods=['DELETE'])
def delete_skill(skill_id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    conn = get_db_connection()
    conn.execute('DELETE FROM skills WHERE id = ?', (skill_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# --- EXPERIENCE ENDPOINTS ---

@app.route('/api/experience', methods=['GET'])
def get_experience():
    conn = get_db_connection()
    experience = conn.execute('SELECT * FROM experience ORDER BY sort_order ASC, id DESC').fetchall()
    conn.close()
    return jsonify([dict(e) for e in experience])

@app.route('/api/experience', methods=['POST'])
def add_experience():
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO experience (company_or_institution, role, duration, description, type, sort_order)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['company_or_institution'], data['role'], data['duration'], 
          data['description'], data['type'], data.get('sort_order', 0)))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"status": "success", "id": new_id})

@app.route('/api/experience/<int:exp_id>', methods=['PUT'])
def update_experience(exp_id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('''
        UPDATE experience 
        SET company_or_institution = ?, role = ?, duration = ?, description = ?, type = ?, sort_order = ?
        WHERE id = ?
    ''', (data['company_or_institution'], data['role'], data['duration'], 
          data['description'], data['type'], data.get('sort_order', 0), exp_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/experience/<int:exp_id>', methods=['DELETE'])
def delete_experience(exp_id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    conn = get_db_connection()
    conn.execute('DELETE FROM experience WHERE id = ?', (exp_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

# --- CONTACT MESSAGES ENDPOINTS ---

@app.route('/api/messages', methods=['POST'])
def add_message():
    data = request.get_json()
    if not data or not data.get('sender_name') or not data.get('sender_email') or not data.get('message_text'):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (sender_name, sender_email, message_text)
        VALUES (?, ?, ?)
    ''', (data['sender_name'], data['sender_email'], data['message_text']))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({"status": "success", "id": new_id})

@app.route('/api/messages', methods=['GET'])
def get_messages():
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
        
    conn = get_db_connection()
    messages = conn.execute('SELECT * FROM messages ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(m) for m in messages])

@app.route('/api/messages/<int:msg_id>', methods=['PUT'])
def update_message(msg_id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
        
    data = request.get_json()
    conn = get_db_connection()
    conn.execute('UPDATE messages SET is_read = ? WHERE id = ?', (data.get('is_read', 0), msg_id))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

@app.route('/api/messages/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    if session.get('role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
        
    conn = get_db_connection()
    conn.execute('DELETE FROM messages WHERE id = ?', (msg_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)