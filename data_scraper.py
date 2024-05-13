import googlemaps
import os
from dotenv import load_dotenv
import re
import time

import sqlite3

# Load environment variables from .env file
load_dotenv()

# Initialize Google Maps API client
gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

# Define fields to extract from the Google Places API
fields = [
            'name',                                         # Name of the place
            'formatted_address',                            # Formatted address of the place
            'rating',                                       # Rating of the place (0.0 to 5.0)
            'opening_hours',                                # Opening hours of the place
            'photo',                                        # URLs to photos of the place
            'geometry',                                     # Geographical location of the place
            'type',                                         # Types/categories of the place
            'price_level',                                  # Price level of the place (0 to 4)
            'user_ratings_total',                           # Total number of user ratings for the place
            'url',                                          # Website URL of the place
            'vicinity',                                     # Vicinity or neighborhood of the place
            'place_id'                                      # Unique identifier for the place
        ]

def to_24_hour(time_unicode):
    '''
    Converts a time string from 12-hour format to 24-hour format
    and returns the opening and closing hours and minutes in 24-hour format
    '''

    # Parse format 10:00 AM - 5:00 PM
    # Split the string into opening and closing times

    # Split by commas, if multiple open close times
    multiple_times = time_unicode.split(',')
    answers = []
    for times in multiple_times:
        split_time = times.split(', ')[0]

        opening_time, closing_time = re.split(r'\s*–\s*', split_time)

        # Split the opening and closing times into hours and minutes
        opening_hour, opening_minute = opening_time.split(':')
        closing_hour, closing_minute = closing_time.split(':')

        # Convert the opening and closing times to 24-hour format
        opening_hour = int(opening_hour)
        closing_hour = int(closing_hour)

        # Convert minutes to integers
        opening_minute = opening_minute.replace('AM', '').replace('PM', '')
        closing_minute = closing_minute.replace('AM', '').replace('PM', '')
        opening_minute = int(opening_minute)
        closing_minute = int(closing_minute)

        # Convert AM/PM to 24-hour format
        if 'PM' in opening_time and opening_hour != 12:
            opening_hour += 12
        if 'PM' in closing_time and closing_hour != 12:
            closing_hour += 12
        
        answers.append((opening_hour, opening_minute, closing_hour, closing_minute))
    
    return answers

def city_exists(city):
    '''
    Checks if a city exists in the database
    '''
    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cities WHERE name = ?", (city,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def clean_data(place_details):
    '''
    Cleans the place details and returns a formatted dictionary
    '''
    
    place_id = place_details['place_id']    
    formatted_details = {}

    # Name
    formatted_details['name'] = place_details.get('name', None)

    # Address
    formatted_details['address'] = place_details.get('formatted_address', None)

    # Rating
    formatted_details['rating'] = place_details.get('rating', None)

    # Opening Hours
    # Extract Monday to Sunday opening hours
    opening_hours = place_details.get('opening_hours', None)

    # Create entries for each day of the week
    if opening_hours:
        days = opening_hours.get('weekday_text', None)
        if days:
            for day in days:
                day, hours = day.split(': ')
                
                if hours == 'Closed':
                    insert_time(place_id, {day: (0, 0, 0, 0)})
                    continue

                if hours == 'Open 24 hours':
                    insert_time(place_id, {day: (0, 0, 23, 59)})
                    continue

                # Extract opening and closing times
                answers = to_24_hour(hours)
                for answer in answers:
                    insert_time(place_id, {day: answer})
    else:
        # Insert None values for all days of the week
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            insert_time(place_id, {day: (None, None, None, None)})

    # Geometry
    geometry = place_details.get('geometry', None)
    if geometry:
        location = geometry.get('location', None)
        if location:
            formatted_details['lat'] = location.get('lat', None)
            formatted_details['lng'] = location.get('lng', None)

    # Types 
    # Accumulate types in one string
    types = place_details.get('types', None)
    if types:
        formatted_details['types'] = ', '.join(types)

        # Insert the categories into the database
        categories = formatted_details['types'].split(',')
        categories = set([category.strip() for category in categories])
        insert_categories(place_id, categories)
    
    # Price Level
    formatted_details['price_level'] = place_details.get('price_level', None)

    # User Ratings Total
    formatted_details['user_ratings_total'] = place_details.get('user_ratings_total', None)

    # url
    formatted_details['url'] = place_details.get('url', None)

    # Vicinity
    formatted_details['vicinity'] = place_details.get('vicinity', None)

    # Place ID
    formatted_details['place_id'] = place_id

    # Photos
    photos = place_details.get('photos', None)
    if photos:
        main_photo = photos[0]
        photo_reference = main_photo.get('photo_reference', None)
        height = main_photo.get('height', None)
        width = main_photo.get('width', None)
        insert_photos(place_id, photo_reference, height, width)
    else:
        insert_photos(place_id, None, None, None)

    return formatted_details
    
def insert_city(city, country):
    '''
    Inserts a city into the database and returns its ID
    '''
    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()

    # Insert the city and country into the database
    sql_command = "INSERT INTO cities (name, country) VALUES (?, ?)"
    cursor.execute(sql_command, (city, country))
    city_id = cursor.lastrowid
    
    conn.commit()
    conn.close()

    return city_id

def insert_place(city_id, attractions):
    '''
    Inserts tourist attractions into the database
    '''
    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()

    # Insert each place from attractions
    for place in attractions:
        # Convert the place dictionary to a list
        values = []
        for val in ['name', 'address', 'rating', 'lat', 'lng', 'types', 'price_level', 'user_ratings_total', 'url', 'vicinity', 'place_id']:
            values.append(place.get(val))
        values.append(city_id)

        sql_command = "INSERT INTO places (name, address, rating, lat, lng, types, price_level, user_ratings_total, url, vicinity, place_id, city_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(sql_command, values)
    
    conn.commit()
    conn.close()

def insert_time(place_id, opening_hours):
    '''
    Inserts opening hours into the database
    '''
    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()

    # Insert each day's opening hours
    for day, hours in opening_hours.items():
        sql_command = "INSERT INTO time (day, open_hour, open_minute, close_hour, close_minute, place_id) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(sql_command, (day, hours[0], hours[1], hours[2], hours[3], place_id))
    
    conn.commit()
    conn.close()

def insert_photos(place_id, photo_reference, height, width):
    '''
    Inserts photos into the database
    '''
    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()

    # Insert the photo into the database
    sql_command = "INSERT INTO photos (photo_reference, height, width, place_id) VALUES (?, ?, ?, ?)"
    cursor.execute(sql_command, (photo_reference, height, width, place_id))
    
    conn.commit()
    conn.close()

def insert_categories(place_id, types):
    '''
    Inserts categories into the database
    '''
    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()

    # Check if the column for the category exists
    cursor.execute(f"PRAGMA table_info(categories)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]

    # Insert the place with appropriate True/False values for each category
    ind = 0
    for category in types:
        if category not in column_names:
            add_category_column(conn, cursor, category)

        # Check if the place is already in the database
        if ind == 0:
            sql_command = f"INSERT INTO categories ({category}, place_id) VALUES (?, ?)"
            cursor.execute(sql_command, (1, place_id))
        else:
            sql_command = f"UPDATE categories SET {category} = ? WHERE place_id = ?"
            cursor.execute(sql_command, (1, place_id))
        ind += 1
    
    conn.commit()
    conn.close()

def add_category_column(conn, cursor, category):
    '''
    Adds a column for a category in the categories table
    '''

    # Add a column for the category
    sql_command = f"ALTER TABLE categories ADD COLUMN {category} INTEGER NULL"
    cursor.execute(sql_command)

    conn.commit()

def categories_including_filter(filters):
    '''
    Returns a list of places filtered by the categories in filters
    '''

    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()

    # Get place_ids of places that have at least one category in filters
    place_ids = set()
    for category in filters:
        cursor.execute(f"SELECT place_id FROM categories WHERE {category} = 1")
        place_ids.update([place[0] for place in cursor.fetchall()])
    
    conn.commit()
    conn.close()
    
    return place_ids

def categories_excluding_filter(filters):
    '''
    Returns a list of places filtered by the categories not in filters
    '''

    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()

    # Get place_ids of places that have at least one category in filters
    place_ids = set()
    for category in filters:
        cursor.execute(f"SELECT place_id FROM categories WHERE {category} = 1")
        place_ids.update([place[0] for place in cursor.fetchall()])
    
    # Get all place_ids
    cursor.execute("SELECT place_id FROM categories")
    all_place_ids = set([place[0] for place in cursor.fetchall()])

    # Get place_ids that are not in filters
    place_ids = all_place_ids - place_ids
    
    conn.commit()
    conn.close()
    
    return place_ids

def clean_matrix(place_ids, matrix):
    '''
    Cleans the distance matrix into distance and time matrix
    '''

    distances = [[0 for _ in range(len(place_ids))] for _ in range(len(place_ids))]
    times = [[0 for _ in range(len(place_ids))] for _ in range(len(place_ids))]

    for i, origin in enumerate(matrix['origin_addresses']):
        for j, destination in enumerate(matrix['destination_addresses']):
            # Get the distance and time between the origin and destination
            distance = matrix['rows'][i]['elements'][j]['distance']['value']
            time = matrix['rows'][i]['elements'][j]['duration']['value']

            # Save distance and time in arrays
            distances[i][j] = distance
            times[i][j] = time

    return distances, times
    

def get_routes(place_ids, mode = 'driving'):
    '''
    Returns a matrix of all distances/times between each pair of places
    Distances in meters, time in seconds
    '''
    # Get longtitude and latitude of each place from the database
    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()

    # Get the places
    cursor.execute("SELECT lat, lng FROM places WHERE place_id IN ({})".format(','.join(['?'] * len(place_ids))), place_ids)
    places = cursor.fetchall()

    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

    # Get the distance between each pair of places

    matrix = gmaps.distance_matrix(places, places, mode = mode)
    distances, times = clean_matrix(place_ids, matrix)
            
    return distances, times

def get_city_country(geocode):
    '''
    Returns the city and country from the geocode
    '''
    city = None
    country = None

    for component in geocode[0]['address_components']:
        if 'locality' in component['types']:
            city = component['long_name']
        if 'country' in component['types']:
            country = component['long_name']
    
    return city, country


def get_attractions_user_input(names):
    '''
    Returns a list of tourist attractions based on user input
    And gets nearby places to each of them
    '''
    attractions = []

    for name in names:
        # Geocode the city to get its coordinates
        geocode_result = gmaps.geocode(name)
        place_location = geocode_result[0]['geometry']['location']

        city, country = get_city_country(geocode_result)

        # Define parameters for nearby search
        params = {
            'location': (place_location['lat'], place_location['lng']),
            'radius': 10000,  # 10 kilometers (adjust as needed)
            'type': 'tourist_attraction'
        }

        places = gmaps.places_nearby(**params)

        #city_in_database = city_exists(city)

        # Extract and return information about tourist attractions
        for place in places['results']:
            # Get place details
            place_id = place['place_id']
            place_details = gmaps.place(place_id = place_id, fields = fields)['result']

            # Clean the place details
            place_details = clean_data(place_details)

            # Add place details to the list
            attractions.append(place_details)
    
    return attractions



def get_tourist_attractions(city):
    '''
    Returns a list of tourist attractions in a city
    '''

    if (city_exists(city)):
        # If the city is already in the database, return the tourist attractions from the database
        conn = sqlite3.connect('Databases/travel.db')
        cursor = conn.cursor()

        # Get all the places with this city
        cursor.execute("SELECT * FROM places WHERE city_id = (SELECT id FROM cities WHERE name = ?)", (city,))
        columns = [column[0] for column in cursor.description]

        # Extract and return information about tourist attractions
        tourist_attractions = []

        for place in cursor.fetchall():
            place_details = dict(zip(columns, place))
            tourist_attractions.append(place_details)
        
        conn.close()
        return tourist_attractions
    
    # Geocode the city to get its coordinates
    geocode_result = gmaps.geocode(city)
    city_location = geocode_result[0]['geometry']['location']
    city, country = get_city_country(geocode_result)

    # Define parameters for nearby search
    params = {
        'location': (city_location['lat'], city_location['lng']),
        'radius': 100000,  # 100 kilometers (adjust as needed)
        'type': 'tourist_attraction'
    }

    tourist_attractions = []

    max_iteration = 2 # Adjust in the future
    iteration = 0

    while iteration < max_iteration:
        # Perform nearby search
        places = gmaps.places_nearby(**params)

        # Extract and return information about tourist attractions
        for place in places['results']:
            # Get place details
            place_id = place['place_id']
            place_details = gmaps.place(place_id = place_id, fields = fields)['result']
            
            # Clean the place details
            place_details = clean_data(place_details)

            # Add place details to the list
            tourist_attractions.append(place_details)
        
        # Check if there are more results to fetch
        if 'next_page_token' in places:
            # Wait for a few seconds before making the next request
            time.sleep(2)
            params['page_token'] = places['next_page_token']
            iteration += 1
        else:
            break
        
    # Insert the city and its places into the database
    city_id = insert_city(city, country)
    insert_place(city_id, tourist_attractions)
    
    return tourist_attractions


if __name__ == '__main__':
    city = 'Paris'
    attractions = get_tourist_attractions(city)

    # Testing get_routes
    #ids = [attractions[i]['place_id'] for i in range(10)]
    #distances, times = get_routes(ids, mode = 'driving')

    # Testing get_attractions_user_input
    #names = ['Eiffel Tower', 'Louvre Museum']
    #attractions = get_attractions_user_input(names)
    #print([attraction['name'] for attraction in attractions])
    

