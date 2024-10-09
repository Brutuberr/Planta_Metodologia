from flask import Flask, request, jsonify, render_template
from datetime import datetime
import sqlite3, pytz, os, random

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


#/plants to see what plants are in the database
@app.route('/plants', methods=['GET'])
def get_plants():
    data, headers = query('plants')
    # return render_template('table.html', rows=rows, headers=headers)
    return jsonify(data), 200

#/plant_types to get the types of plants
@app.route('/plant_types', methods=['GET'])
def get_plant_types():
    data, headers = query('plant_types')
    # return render_template('table.html', rows=rows, headers=headers)
    return jsonify(data), 200

#/users to get a list of all users
@app.route('/users', methods=['GET'])
def get_users():
    data, headers = query('users')
    # return render_template('table.html', rows=rows, headers=headers)
    return jsonify(data), 200

#/data gets all of the entries in the data table
@app.route('/data', methods=['GET'])
def get_data():
    # rows, headers = query('data')
    # # Convert date_added from UTC to local time for each row
    # for row in rows:
    #     row['date_added'] = convert_to_local_time(row.get('date_added'))
    # return render_template('table.html', rows=rows, headers=headers)

    data, headers = query('data')

    for row in data:
        row['date_added'] = convert_to_local_time(row['date_added'])

    return jsonify(data), 200

#/data/<plant_id> gets entries for a specific plant
@app.route('/data/<plant_id>', methods=['GET'])
def get_data_specific(plant_id):
    data, headers = query('data', where=plant_id)

    # Convert date_added from UTC to local time for each row
    for row in data:
        row['date_added'] = convert_to_local_time(row.get('date_added'))

    # return render_template('table.html', rows=rows, headers=headers)

    return jsonify(data), 200

# logs plant data
# usage example: POST {plant_id=2, soil_humidity=134.42, light_level=835.43, temperature=23.42}
@app.route('/logdata', methods=['POST'])
def log_data():
    data = request.get_json()  # Get JSON data from the request
    plant_id = data.get('plant_id')
    hum = data.get('soil_humidity')
    luz = data.get('light_level')
    temp = data.get('temperature')

    if not plant_id:
        return jsonify({'error': 'Plant id is required'}), 400
    if not hum:
        return jsonify({'error': 'Humidity is required'}), 400
    if not luz:
        return jsonify({'error': 'Light level is required'}), 400
    if not temp:
        return jsonify({'error': 'Temperature is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('INSERT INTO data (plant_id, soil_humidity, light_level, temperature) VALUES (?, ?, ?, ?)', (plant_id, hum, luz, temp))
    conn.commit()

    new_data_id = cursor.lastrowid  # Get the ID of the newly inserted row

    conn.close()

    return jsonify({'id': new_data_id, 'plant_id': plant_id, 'Humidity': hum, 'Light Level': luz, 'Temperature': temp}), 201

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

@app.route('/create_data/<ammount>', methods=["GET"])
def create_data(ammount):
    conn = get_db_connection()
    
    for id in range(5):
        plant_id = id + 1
        for i in range(int(ammount)):
            soil_humidity = random.randint(200, 3000)
            light_level = random.randint(100, 1000)
            temperature = random.randint(-8, 40)

            conn.cursor().execute('INSERT INTO data (plant_id, soil_humidity, light_level, temperature) VALUES (?, ?, ?, ?)', (plant_id, soil_humidity, light_level, temperature))
            conn.commit()

    return(f"Created {ammount} more entries for ids 1-5 \n"), 201


def create_db():
    if not os.path.exists('test.db'):

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password TEXT DEFAULT ""
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            plant_id INTEGER NOT NULL,
            soil_humidity REAL NOT NULL,
            light_level REAL NOT NULL,
            temperature REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS plants (
            plant_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id INTEGER NOT NULL,
            plantType_id INTEGER NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS plant_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,  -- Fixed: Corrected 'PRIMERY' to 'PRIMARY'
            nombre TEXT NOT NULL,
            max_hum REAL NOT NULL,
            min_hum REAL NOT NULL,
            max_temp REAL NOT NULL,
            min_temp REAL NOT NULL,
            max_luz REAL NOT NULL,
            min_luz REAL NOT NULL
        )
        ''')

        conn.commit()
        conn.close()

        print("Database created ", 201)

        create_data(5)
        return
    
    print("Database already exists ", 418)


PORT = os.environ['PORT']

if PORT == None:
    PORT = 8080

debug = os.environ['DEBUG']

if debug == '1':
    debug = True
else:
    debug = False

if __name__ == '__main__':
    app.run(debug=debug, host='0.0.0.0', port=PORT)

