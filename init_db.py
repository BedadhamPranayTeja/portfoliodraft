# init_db.py
import sqlite3

connection = sqlite3.connect('portfolio.db')
cursor = connection.cursor()

# Create the projects table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        tech_stack TEXT NOT NULL
    )
''')

# Insert some initial project data
projects = [
    ('Web-Integrated Robotics Controller', 'A hardware-software integration project allowing web-based control of robotic movements.', 'React, Flask, C++'),
    ('Full-Stack Hackathon Dashboard', 'A complete web application built during a 24-hour sprint with role-based auth.', 'React, Node, SQLite'),
    ('Algorithmic Pathfinding Robot', 'A heavy-logic robotics project focusing on efficient maze navigation.', 'Python, C'),
]

cursor.executemany('INSERT INTO projects (title, description, tech_stack) VALUES (?, ?, ?)', projects)

connection.commit()
connection.close()
print("Database initialized successfully.")