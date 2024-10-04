from flask import Flask, request, jsonify, render_template # type: ignore
import sqlite3
from datetime import datetime
import pytz

app = Flask(__name__)

DATABASE = 'test.db'

# Time zone settings
local_tz = pytz.timezone('America/Argentina/Buenos_Aires') 

# Database connection
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize the database
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
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS data (
        plant_id INTEGER,
        soil_humidity REAL,
        light_level REAL,
        temperature REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
# init_db()

def query(table, where = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if where != None:
        cursor.execute(f'SELECT * FROM {table} WHERE plant_id = ?', (where))
    else:
        cursor.execute(f'SELECT * FROM {table}')
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    results = [dict(row) for row in rows]
    
    # Get column headers
    headers = results[0].keys() if results else []
    
    conn.close()

    return results, headers

def convert_to_local_time(utc_timestamp):
    # Convert a UTC timestamp to local time (GMT-4)
    if not utc_timestamp:
        return None
    utc_time = datetime.strptime(utc_timestamp, '%Y-%m-%d %H:%M:%S')
    utc_time = pytz.utc.localize(utc_time)
    local_time = utc_time.astimezone(local_tz)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

@app.route('/plants', methods=['GET'])
def get_plants():
    rows, headers = query('plants')
    return render_template('table.html', rows=rows, headers=headers)

@app.route('/plant_types', methods=['GET'])
def get_plant_types():
    rows, headers = query('plant_types')
    return render_template('table.html', rows=rows, headers=headers)

@app.route('/users', methods=['GET'])
def get_users():
    rows, headers = query('users')
    return render_template('table.html', rows=rows, headers=headers)

@app.route('/data', methods=['GET'])
def get_data():
    rows, headers = query('data')
    # Convert date_added from UTC to local time for each row
    for row in rows:
        row['date_added'] = convert_to_local_time(row.get('date_added'))
    return render_template('table.html', rows=rows, headers=headers)

@app.route('/data/<plant_id>', methods=['GET'])
def get_data_specific(plant_id):
    rows, headers = query('data', where=plant_id)
    # Convert date_added from UTC to local time for each row
    for row in rows:
        row['date_added'] = convert_to_local_time(row.get('date_added'))
    return render_template('table.html', rows=rows, headers=headers)

@app.route('/logdata', methods=['POST'])
def log_data():
    data = request.get_json()  # Get JSON data from the request
    plant_id = data.get('plant_id')
    humendad = data.get('soil_humidity')
    luz = data.get('light_level')
    temperatura = data.get('temperature')

    if not plant_id:
        return jsonify({'error': 'Plant id is required'}), 400
    if not humendad:
        return jsonify({'error': 'Humidity is required'}), 400
    if not luz:
        return jsonify({'error': 'Light level is required'}), 400
    if not temperatura:
        return jsonify({'error': 'Temperature is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO data (plant_id, soil_humidity, light_level, temperature) VALUES (?, ?, ?, ?)', (plant_id, humendad, luz, temperatura))
    conn.commit()

    new_data_id = cursor.lastrowid  # Get the ID of the newly inserted row

    conn.close()

    return jsonify({'id': new_data_id, 'plant_id': plant_id, 'Humidity': humendad, 'Light Level': luz, 'Temperature': temperatura}), 201

@app.route('/addplant', methods=['POST'])
def add_plant():
    data = request.get_json()  # Get JSON data from the request
    user_id = data.get('user_id')
    plantType = data.get('plantType')

    if not user_id:
        return jsonify({'error': 'User ID is required'}), 400
    
    if not plantType:
        return jsonify({'error': 'Plant type id is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO plants (user_id, plantType_id) VALUES (?, ?)', (user_id, plantType))
    conn.commit()

    new_plant_id = cursor.lastrowid  # Get the ID of the newly inserted row

    conn.close()

    return jsonify({'plant_id': new_plant_id, 'user_id': user_id, 'plantType_id': plantType}), 201

if __name__ == '__main__':
    app.run(debug=True)
