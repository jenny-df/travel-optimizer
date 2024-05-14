from flask import Flask, render_template, request, url_for, redirect
import os
from dotenv import load_dotenv
from data_scraper import *
from routing_basic import *


app = Flask(__name__,
	template_folder='templates', 
	static_folder='static'
)

app.config.from_pyfile('config.py')
load_dotenv()

categories = {
    "Park": "park",
    "Casino": "casino",
    "Museum": "museum",
    "Night Club": "night_club",
    "Library": "library",
    "Place of Worship": "place_of_worship",
    "Book Store": "book_store",
    "Cemetery": "cemetery",
    "Stadium": "stadium",
    "Zoo": "zoo",
    "Aquarium": "aquarium",
    "Art Gallery": "art_gallery",
    "Restaurant": "restaurant",
    "Bar": "bar",
    "Bakery": "bakery",
    "Clothing Store": "clothing_store",
    "Spa": "spa",
    "Amusement Park": "amusement_park",
}

valid_categories = set(categories.values())

GOOGLE_KEY = os.getenv('GOOGLE_MAPS_API_KEY')

@app.route('/', methods = ["GET"])
def home():
    return render_template("home.html")


@app.route('/data', methods = ["GET"])
def data():
    return render_template("data.html", categories=categories, google_key=GOOGLE_KEY)


@app.route('/results', methods = ["POST"])
def results():
    # Getting values from the form
    data = dict(request.form)
    data['must_locations'] = [tuple(info.split("$")) for info in data['must_locations'].split('*')]
    data['must_names'] = data['must_names'].split('$')
    tmp = data['hotel'].split("$")
    data['hotel_loc'] = (tmp[0], tmp[1])
    data['hotel_name'] = tmp[2]

    # Reformatting categories chosen by user
    data['include'] = []
    data['exclude'] = []
    for key in data:
        if key in valid_categories:
            data[data[key]].append(key)

    # Deleting unnecessary data
    to_del = data['include'] + data['exclude'] + ['Submit', 'location_search', 'hotel_input']
    for key in to_del:
        del data[key]

    # Getting the required and optional locations based on data
    required, optional = get_attractions_user_input(data)

    # Call to optimized routing
    optimized_route_output, total_trip_time = router(required, optional, data['ranking_considered'] == "yes", data['transport'], int(data['numDays']))

    return render_template("results.html", 
                        routes = optimized_route_output,
                        total_trip_time = total_trip_time,
                        required = required,
                        optional = optional,
                        google_key = GOOGLE_KEY,
                        )


@app.route('/scrape/<string:city_name>', methods = ["GET"])
def scrape(city_name):
    # CHANGE TO GET if you want to use this!
    try:
        info = get_tourist_attractions(city_name)
        print(info)
    except:
        print("ERROR in scraping")
    
    return redirect(url_for('home', _method="GET"))


@app.route('/<path:other_path>', methods=['GET', 'POST'])
def catch_all(other_path):
	return render_template('404.html', error = "This route doesn't exist")


if __name__ == '__main__':
	app.run(debug = True, port=8081)