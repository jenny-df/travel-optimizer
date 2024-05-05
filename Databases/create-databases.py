import sqlite3

def create_cities_table():
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()

    # Create the table with the required fields
    sql_command = f"CREATE TABLE IF NOT EXISTS cities (     \
                    id INTEGER PRIMARY KEY,                 \
                    name TEXT UNIQUE                        \
                    )"

    # Execute the SQL command
    cursor.execute(sql_command)
    conn.commit()
    conn.close()

def create_places_table():
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()

    # Create places table
    sql_command = f"CREATE TABLE IF NOT EXISTS places (              \
                    id INTEGER PRIMARY KEY,                          \
                    name TEXT,                                       \
                    address TEXT NULL,                               \
                    rating REAL NULL,                                \
                    lat REAL,                                        \
                    lng REAL,                                        \
                    types TEXT NULL,                                 \
                    price_level INTEGER NULL,                        \
                    user_ratings_total INTEGER NULL,                 \
                    url TEXT NULL,                                   \
                    vicinity TEXT NULL,                              \
                    place_id TEXT UNIQUE NULL,                       \
                    city_id INTEGER,                                 \
                    FOREIGN KEY (city_id) REFERENCES cities(id)      \
                    )"
    
    cursor.execute(sql_command)
    conn.commit()
    conn.close()

def create_time_table():
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()

    # Create the table with the required fields
    sql_command = f"CREATE TABLE IF NOT EXISTS time (               \
                    id INTEGER PRIMARY KEY,                         \
                    day TEXT,                                       \
                    open_hour INTEGER NULL,                         \
                    open_minute INTEGER NULL,                       \
                    close_hour TEXT NULL,                           \
                    close_minute TEXT NULL,                         \
                    place_id INTEGER,                               \
                    FOREIGN KEY (place_id) REFERENCES places(id)    \
                    )"

    # Execute the SQL command
    cursor.execute(sql_command)
    conn.commit()
    conn.close()

def create_photos_table():
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()

    # Create the table with the required fields
    sql_command = f"CREATE TABLE IF NOT EXISTS photos (     \
                    id INTEGER PRIMARY KEY,                  \
                    photo TEXT,                               \
                    place_id INTEGER,                         \
                    FOREIGN KEY (place_id) REFERENCES places(id) \
                    )"

    # Execute the SQL command
    cursor.execute(sql_command)
    conn.commit()
    conn.close()

def create_photos_table():
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()

    # Create the table with the required fields
    sql_command = f"CREATE TABLE IF NOT EXISTS photos (             \
                    id INTEGER PRIMARY KEY,                         \
                    photo_reference TEXT NULL,                      \
                    height INTEGER NULL,                            \
                    width INTEGER NULL,                             \
                    place_id INTEGER,                               \
                    FOREIGN KEY (place_id) REFERENCES places(id)    \
                    )"

    # Execute the SQL command
    cursor.execute(sql_command)
    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_cities_table()
    create_places_table()
    create_time_table()
    create_photos_table()