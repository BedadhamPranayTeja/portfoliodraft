# app.py
from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('portfolio.db')
    conn.row_factory = sqlite3.Row  # Returns rows as dictionaries
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

if __name__ == '__main__':
    app.run(debug=True,port=5001)