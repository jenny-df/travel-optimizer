import sqlite3

def create_cities_table():
    '''
    Creates a table to store which cities have already been scraped
    '''
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()

    # Create the table with the required fields
    sql_command = f"CREATE TABLE IF NOT EXISTS cities (     \
                    id INTEGER PRIMARY KEY,                 \
                    name TEXT,                              \
                    country TEXT                            \
                    )"

    # Execute the SQL command
    cursor.execute(sql_command)
    conn.commit()
    conn.close()

def create_places_table():
    '''
    Creating a table to store the places that have already been scraped
    '''
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
    '''
    Creating a table to store the opening and closing times of the places
    '''
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()

    # Create the table with the required fields
    sql_command = f"CREATE TABLE IF NOT EXISTS time (               \
                    id INTEGER PRIMARY KEY,                         \
                    day TEXT,                                       \
                    open_hour INTEGER NULL,                         \
                    open_minute INTEGER NULL,                       \
                    close_hour INTEGER NULL,                           \
                    close_minute INTEGER NULL,                         \
                    place_id TEXT,                                  \
                    FOREIGN KEY (place_id) REFERENCES places(id)    \
                    )"

    # Execute the SQL command
    cursor.execute(sql_command)
    conn.commit()
    conn.close()

def create_photos_table():
    '''
    Creating a table to store the photos of the places
    '''
    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()

    # Create the table with the required fields
    sql_command = f"CREATE TABLE IF NOT EXISTS photos (             \
                    id INTEGER PRIMARY KEY,                         \
                    photo TEXT,                                     \
                    place_id TEXT,                                  \
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
    sql_command = f"CREATE TABLE IF NOT EXISTS photos (             \
                    id INTEGER PRIMARY KEY,                         \
                    photo_reference TEXT NULL,                      \
                    height INTEGER NULL,                            \
                    width INTEGER NULL,                             \
                    place_id TEXT,                                  \
                    FOREIGN KEY (place_id) REFERENCES places(id)    \
                    )"

    # Execute the SQL command
    cursor.execute(sql_command)
    conn.commit()
    conn.close()


def create_category_table():
    '''
    Divides the categories column in the places table into a separate table
    With each unique category as a one separate column
    '''

    conn = sqlite3.connect('travel.db')
    cursor = conn.cursor()

    # Create categories table with every field in categories as a column
    create_table_query = "CREATE TABLE IF NOT EXISTS categories (place_id TEXT PRIMARY KEY, FOREIGN KEY (place_id) REFERENCES places(id))"
    cursor.execute(create_table_query)

    conn.commit()
    conn.close()



if __name__ == '__main__':
    create_cities_table()
    create_places_table()
    create_time_table()
    create_photos_table()
    create_category_table()