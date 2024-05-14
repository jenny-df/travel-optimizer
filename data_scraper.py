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

time_spent_per_category = {'Park': 120, 'Casino': 240, 'Museum': 180, 'Night Club': 180, 'Library': 60, 'Place of Worship': 45.0, 'Book Store': 30.0, 'Cemetery': 90.0, 
'Stadium': 180, 'Zoo': 180, 'Aquarium': 150.0, 'Art Gallery': 120, 'Restaurant': 90.0, 'Bar': 90.0, 'Bakery': 30.0, 'Clothing Store': 30.0, 'Spa': 180, 'Amusement Park': 420}

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

def input_time_to_int(time_str):
    '''
    Converts a time string to an integer
    '''
    hour, minute = time_str.split(':')
    hour = int(hour)
    minute = int(minute)

    return hour * 60 + minute

def sleep_time_truncate(sleep_time, wake_time, open_time, close_time):
    '''
    Truncates the open/close times according to the sleep time
    '''

    open_time = max(open_time, wake_time)
    close_time = min(close_time, sleep_time)

    return open_time, close_time

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
    
    time_details = []
    photo_details = []
    category_details = []


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
                    time_details.append([place_id, {day: (0, 0, 0, 0)}])
                    #insert_time(place_id, {day: (0, 0, 0, 0)})
                    continue

                if hours == 'Open 24 hours':
                    time_details.append([place_id, {day: (0, 0, 23, 59)}])
                    #insert_time(place_id, {day: (0, 0, 23, 59)})
                    continue

                # Extract opening and closing times
                answers = to_24_hour(hours)
                for answer in answers:
                    time_details.append([place_id, {day: answer}])
                    #insert_time(place_id, {day: answer})
    else:
        # Insert None values for all days of the week
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            time_details.append([place_id, {day: (None, None, None, None)}])
            #insert_time(place_id, {day: (None, None, None, None)})

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
        category_details.append([place_id, categories])
        #insert_categories(place_id, categories)
    
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
        photo_details.append([place_id, photo_reference, height, width])
        #insert_photos(place_id, photo_reference, height, width)
    else:
        photo_details.append([place_id, None, None, None])
        #insert_photos(place_id, None, None, None)

    return [formatted_details, time_details, photo_details, category_details]
    
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

def update_place(city_id, attractions):
    '''
    Updates tourist attractions in the database
    Adds non-existent ones and skips others
    '''

    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()

    # Get all the place_ids already in the city
    cursor.execute("SELECT place_id FROM places WHERE city_id = ?", (city_id,))
    place_ids = set([place[0] for place in cursor.fetchall()])

    # Insert places

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

def categories_including_filter(all_place_ids, filters):
    '''
    Returns a list of places filtered by the categories in filters
    '''

    if not filters:
        return all_place_ids

    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()
    #all_place_id_str = ', '.join(['?'] * len(all_place_ids))
    query = f"SELECT place_id FROM categories WHERE {' OR '.join([f'{category} = 1' for category in filters])} AND place_id IN ({', '.join(['?'] * len(all_place_ids))})"
    cursor.execute(query, all_place_ids)
    place_ids = set([place[0] for place in cursor.fetchall()])
    
    conn.commit()
    conn.close()
    
    return list(place_ids)

def categories_excluding_filter(all_place_ids, filters):
    '''
    Returns a list of places filtered by the categories not in filters
    '''
    if not filters:
        return all_place_ids
    
    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()
    all_place_id_str = ', '.join(['?' for _ in range(len(all_place_ids))])
    query = f"SELECT place_id FROM categories WHERE {' AND '.join([f'{category} = 1' for category in filters])} AND place_id IN ({', '.join(['?'] * len(all_place_ids))})"
    cursor.execute(query, all_place_ids)
    place_ids = set([place[0] for place in cursor.fetchall()])
    place_ids = set(all_place_ids) - place_ids
    
    conn.commit()
    conn.close()
    
    return list(place_ids)

def budget_filter(all_place_ids, budget):
    '''
    Returns a list of places filtered by the budget
    '''
    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()
    query = f"SELECT place_id FROM places WHERE (price_level <= ? OR price_level IS NULL) AND place_id IN ({', '.join(['?'] * len(all_place_ids))})"
    cursor.execute(query, (budget, all_place_ids))
    place_ids = set([place[0] for place in cursor.fetchall()])
    
    conn.commit()
    conn.close()
    
    return list(place_ids)

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
            time_X = matrix['rows'][i]['elements'][j]['duration']['value']

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


def get_average_time(place_id):
    '''
    Get average time spent at a place based on the categories of the place
    '''
    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM categories WHERE place_id = ?", (place_id,))
    categories = cursor.fetchone()
    time_spent = 0
    counter = 0
    for category in categories:
        if category == 1:
            if category not in time_spent_per_category:
                continue
            time_spent += time_spent_per_category[category]
            counter += 1
    
    if counter != 0:
        return time_spent / counter
    else:
        return 60 # 1 hour default




def get_routes_simple(place_ids, sleep_time, wake_time, filters_including, filters_excluding):
    '''
    Returns longtitude latitude of the places with these ids
    '''

    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()

    place_ids = categories_including_filter(place_ids, filters_including)
    place_ids = categories_excluding_filter(place_ids, filters_excluding)

    # Get the places
    cursor.execute("SELECT place_id, name, lat, lng FROM places WHERE place_id IN ({})".format(','.join(['?'] * len(place_ids))), place_ids)
    places = cursor.fetchall()


    # Get opening close times of the places
    cursor.execute("SELECT place_id, day, open_hour, open_minute, close_hour, close_minute FROM time WHERE place_id IN ({})".format(','.join(['?'] * len(place_ids))), place_ids)
    times = cursor.fetchall()

    # Truncate to min opening hour min opening max close hour max close min for each place over all weeks
    # Calculate the mind opening time and max closing time for each place_id
    truncated_times = {}
    for time in times:
        place_id, day, open_hour, open_minute, close_hour, close_minute = time
        if not truncated_times.get(place_id):
            truncated_times[place_id] = [24, 60, 0, 0]

        if open_hour is None:
            truncated_times[place_id][0] = 9
            truncated_times[place_id][1] = 0
            truncated_times[place_id][2] = 17
            truncated_times[place_id][3] = 0
        elif open_hour == 0 and open_minute == 0 and close_minute == 0 and close_hour == 0:
            continue
        elif open_hour < truncated_times[place_id][0]:
            truncated_times[place_id][0] = open_hour
            truncated_times[place_id][1] = open_minute
        elif open_hour == truncated_times[place_id][0] and open_minute < truncated_times[place_id][1]:
            truncated_times[place_id][1] = open_minute
        elif close_hour > truncated_times[place_id][2]:
            truncated_times[place_id][2] = close_hour
            truncated_times[place_id][3] = close_minute
        elif close_hour == truncated_times[place_id][2] and close_minute > truncated_times[place_id][3]:
            truncated_times[place_id][3] = close_minute
    
    for place_id in truncated_times:
        truncated_times[place_id] = [truncated_times[place_id][0] * 60 + truncated_times[place_id][1], truncated_times[place_id][2] * 60 + truncated_times[place_id][3]]
        truncated_times[place_id] = sleep_time_truncate(sleep_time, wake_time, truncated_times[place_id][0], truncated_times[place_id][1])

    ans = []
    for place in places:
        open, close = truncated_times[place[0]]
        if open > 1440:
            open = 1440
        if close > 1440:
            close = 1440
        avg = get_average_time(place[0])
        ans.append((place[0], place[1], place[2], place[3], open, close, avg))
    
    conn.commit()
    conn.close()

    return ans

def get_city_country(lat, lng):
    '''
    Returns the city and country from the latitude and longtitude
    '''

    reverse_geocode = gmaps.reverse_geocode((lat, lng))
    city = None
    country = None

    for component in reverse_geocode[0]['address_components']:
        if 'locality' in component['types']:
            city = component['long_name']
        if 'country' in component['types']:
            country = component['long_name']
    
    return city, country
    

def get_attractions_user_input(info):
    '''
    Returns a list of tourist attractions based on user input
    And gets nearby places to each of them
    List of longtitudes and latitudes
    '''
    required_locations = info['must_locations']
    required_names = set(info['must_names'])
    sleep_time, wake_time = input_time_to_int(info['sleepTime']), input_time_to_int(info['wakeTime'])
    filters_including = info['include']
    filters_excluding = info['exclude']
    
    required_attractions = set()
    optional_attractions = set()
    places_unique = set()

    max_iteration = 5 # Adjust in the future
    iteration = 0

    conn = sqlite3.connect('Databases/travel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT place_id FROM places")
    all_ids = cursor.fetchall()
    places_unique = set([place[0] for place in all_ids])
    conn.commit()
    conn.close()

    for lat, lng in required_locations:
        city, country = get_city_country(lat, lng)
        if city_exists(city):
            # Get the place_ids in the city
            conn = sqlite3.connect('Databases/travel.db')
            cursor = conn.cursor()
            cursor.execute("SELECT place_id, city_id FROM places WHERE city_id = (SELECT id FROM cities WHERE name = ?)", (city,))
            all_places = cursor.fetchall()
            place_ids = [place[0] for place in all_places]
            print(all_places)
            city_id = all_places[0][1]
            places_unique.update(place_ids)
            optional_attractions.update(place_ids)
            conn.commit()
            conn.close()
        else:
            city_id = insert_city(city, country)

        # Define parameters for nearby search
        params = {
            'location': (lat, lng),
            'radius': 20000,  # 20 kilometers (adjust as needed)
            'type': 'tourist_attraction'
        }

        places = gmaps.places_nearby(**params)

        # Extract and return information about tourist attractions
        for place in places['results']:
            # Get place details
            place_id = place['place_id']

            if (place['name'] in required_names):
                required_attractions.add(place_id)      

            if place_id in places_unique:
                continue                

            places_unique.add(place_id)
            optional_attractions.add(place_id)
            place_details = gmaps.place(place_id = place_id, fields = fields)['result']

            # Clean the place details
            formatted_details, time_details, photo_details, category_details  = clean_data(place_details)
            # Insert everything in the database
            insert_place(city_id, [formatted_details])
            for time in time_details:
                insert_time(time[0], time[1])
            for photo in photo_details:
                insert_photos(photo[0], photo[1], photo[2], photo[3])
            for category in category_details:
                insert_categories(category[0], category[1])

        # Get the details of lan and lng
        req_place = gmaps.reverse_geocode((lat, lng))
        req_id = req_place[0]['place_id']
        req_details = gmaps.place(place_id = req_id, fields = fields)['result']
        formatted_details, time_details, photo_details, category_details  = clean_data(req_details)
        required_attractions.add(req_id)

        if req_id not in places_unique:
            places_unique.add(req_id)
            optional_attractions.add(req_id)
            insert_place(city_id, [formatted_details])
            for time in time_details:
                insert_time(time[0], time[1])
            for photo in photo_details:
                insert_photos(photo[0], photo[1], photo[2], photo[3])
            for category in category_details:
                insert_categories(category[0], category[1])



    # Remove required attractions from optional attractions
    optional_attractions = optional_attractions - required_attractions

    required_info = [('HOTEL', info['hotel_name'], info['hotel_loc'][0], info['hotel_loc'][1], 0, 1440, 0)] + get_routes_simple(list(required_attractions), sleep_time, wake_time, [], [])
    optional_info = get_routes_simple(list(optional_attractions), sleep_time, wake_time, filters_including, filters_excluding)
    return required_info, optional_info



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
    names = {'must_locations': [('42.3600825', '-71.0588801')], 'must_names': ['Boston'], 'ranking_considered': 'yes', 'transport': 'car', 'budget': '1231231', 'hotel_name': 'balbla', 'hotel_loc': ('42.3484914', '-71.0952429'), 'sleepTime': '22:21', 'wakeTime': '10:24', 'arrivalDate': '2024-05-14', 'arrivalTime': '13:21', 'numDays': '5', 'include': ['stadium', 'museum'], 'exclude': []}
    required, optional = get_attractions_user_input(names)

    ids = [place[0] for place in optional]

    filters = ['museum']

    print(optional)

    #new = categories_including_filter(ids, filters)
    #print(ids)
    #print()
    #print()
    #print(new)
    #print(len(required), len(optional))
