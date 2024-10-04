import random, sqlite3

reps = input("How many entries should the program create per id? ")
ids = input("Ids from 1 to : ")

conn = sqlite3.connect('test.db')

for id in range(int(ids)):
    plant_id = id + 1
    for i in range(int(reps)):
        soil_humidity = random.randint(200, 3000)
        light_level = random.randint(100, 1000)
        temperature = random.randint(-8, 40)

        conn.cursor().execute('INSERT INTO data (plant_id, soil_humidity, light_level, temperature) VALUES (?, ?, ?, ?)', (plant_id, soil_humidity, light_level, temperature))
        conn.commit()


conn.close()
