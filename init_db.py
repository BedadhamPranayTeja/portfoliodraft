# init_db.py
import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect('portfolio.db')
cursor = connection.cursor()

# Drop existing tables to ensure a clean new schema
cursor.execute('DROP TABLE IF EXISTS projects')
cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('DROP TABLE IF EXISTS profile')
cursor.execute('DROP TABLE IF EXISTS skills')
cursor.execute('DROP TABLE IF EXISTS experience')
cursor.execute('DROP TABLE IF EXISTS messages')

# 1. Create the projects table with extra fields
cursor.execute('''
    CREATE TABLE projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        tech_stack TEXT NOT NULL,
        image_url TEXT,
        github_url TEXT,
        live_url TEXT,
        featured INTEGER DEFAULT 0
    )
''')

# 2. Create the users table for admin authentication
cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
''')

# 3. Create the profile table for customizable branding info
cursor.execute('''
    CREATE TABLE profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        title TEXT NOT NULL,
        bio TEXT NOT NULL,
        profile_picture TEXT,
        github_link TEXT,
        linkedin_link TEXT,
        email TEXT,
        resume_url TEXT
    )
''')

# 4. Create the skills table
cursor.execute('''
    CREATE TABLE skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        proficiency INTEGER DEFAULT 80
    )
''')

# 5. Create the experience table
cursor.execute('''
    CREATE TABLE experience (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_or_institution TEXT NOT NULL,
        role TEXT NOT NULL,
        duration TEXT NOT NULL,
        description TEXT NOT NULL,
        type TEXT NOT NULL, -- 'work' or 'education'
        sort_order INTEGER DEFAULT 0
    )
''')

# 6. Create the messages table for visitor contacts
cursor.execute('''
    CREATE TABLE messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_name TEXT NOT NULL,
        sender_email TEXT NOT NULL,
        message_text TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_read INTEGER DEFAULT 0
    )
''')

# --- Seed Initial Data ---

# Profile Seed
cursor.execute('''
    INSERT INTO profile (name, title, bio, profile_picture, github_link, linkedin_link, email, resume_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', (
    'Pranay Teja Bedadham',
    'Robotics Engineer & Full-Stack Developer',
    'B.Tech student passionate about autonomous systems, embedded electronics, and crafting high-performance web applications. I bridge the gap between physical hardware and cloud software.',
    'https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&q=80&w=400',
    'https://github.com/',
    'https://linkedin.com/',
    'pranay@example.com',
    '#'
))

# Projects Seed
projects_data = [
    ('Autonomous Pathfinding Robot', 
     'Developed an autonomous maze-navigating robot utilizing LiDAR mapping, ROS2 navigation stack, and dynamic Dijkstra algorithms.', 
     'C++, ROS2, LiDAR, Python, Raspberry Pi',
     'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?auto=format&fit=crop&q=80&w=600',
     'https://github.com/',
     '',
     1),
    ('Full-Stack Control Dashboard', 
     'Real-time web application to monitor, teleoperate, and collect telemetry data from hardware nodes over WebSockets.', 
     'React, Node.js, WebSockets, TailwindCSS, SQLite',
     'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=600',
     'https://github.com/',
     'https://dashboard.example.com',
     1),
    ('Computer Vision Sorting Arm', 
     '6-DOF robotic arm integrated with OpenCV object detection to categorize and sort inventory items by size and color.', 
     'Python, OpenCV, Arduino, CAD/SolidWorks',
     'https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&q=80&w=600',
     'https://github.com/',
     '',
     0)
]
cursor.executemany('''
    INSERT INTO projects (title, description, tech_stack, image_url, github_url, live_url, featured)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', projects_data)

# Skills Seed
skills_data = [
    ('Python', 'Languages', 90),
    ('C++', 'Languages', 85),
    ('JavaScript', 'Languages', 80),
    ('SQL', 'Languages', 75),
    ('HTML/CSS', 'Languages', 90),
    ('React', 'Frameworks / Libs', 85),
    ('Flask', 'Frameworks / Libs', 80),
    ('ROS2', 'Frameworks / Libs', 80),
    ('OpenCV', 'Frameworks / Libs', 75),
    ('Node.js', 'Frameworks / Libs', 70),
    ('Git', 'Hardware / Tools', 85),
    ('Arduino', 'Hardware / Tools', 90),
    ('Raspberry Pi', 'Hardware / Tools', 85),
    ('CAD/SolidWorks', 'Hardware / Tools', 75),
    ('Docker', 'Hardware / Tools', 65)
]
cursor.executemany('''
    INSERT INTO skills (name, category, proficiency)
    VALUES (?, ?, ?)
''', skills_data)

# Experience Seed
experience_data = [
    ('RoboTech Labs', 'Robotics Engineering Intern', 'May 2025 - July 2025', 
     'Collaborated on designing firmware controllers for low-latency motors. Integrated ROS2 messaging namespaces across multiple compute nodes.', 
     'work', 0),
    ('B.Tech Technical Club', 'Project Lead', '2024 - Present', 
     'Led a team of 8 students to build a solar-powered telemetry crawler. Implemented dynamic pathfinding and sensor data visualization.', 
     'work', 1),
    ('University Institute of Technology', 'Bachelor of Technology in Engineering', '2023 - 2027', 
     'Focusing on Robotics, Embedded Systems, and Software Engineering. GPA: 8.8/10.0', 
     'education', 2)
]
cursor.executemany('''
    INSERT INTO experience (company_or_institution, role, duration, description, type, sort_order)
    VALUES (?, ?, ?, ?, ?, ?)
''', experience_data)

# Admin User Seed
admin_password_hash = generate_password_hash('admin123')
cursor.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', ('admin', admin_password_hash))

connection.commit()
connection.close()
print("Database initialized successfully with complete tables and seeded values.")