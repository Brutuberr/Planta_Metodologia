from flask import Flask, request, jsonify # type: ignore
import sqlite3

app = Flask(__name__)

# Database file path
DATABASE = 'test.db'

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows dict-like access to rows
    return conn

# Function to initialize the database and create a table
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER
    )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
# init_db()

@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM plants')
    rows = cursor.fetchall()
    
    # Convert rows to list of dictionaries
    users = [dict(row) for row in rows]
    
    conn.close()
    return jsonify(users)

@app.route('/users', methods=['POST'])
def add_user():
    data = request.get_json()  # Get JSON data from the request
    name = data.get('name')
    sc_name = data.get('sc_name')

    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('INSERT INTO plants (name, sc_name) VALUES (?, ?)', (name, sc_name))
    conn.commit()
    
    new_user_id = cursor.lastrowid  # Get the ID of the newly inserted row
    
    conn.close()
    
    return jsonify({'id': new_user_id, 'name': name, 'sc_name': sc_name}), 201

if __name__ == '__main__':
    app.run(debug=True)
