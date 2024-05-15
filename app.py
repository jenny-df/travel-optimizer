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

def preprocess_data(data):
     # Reformating
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

    return data

@app.route('/', methods = ["GET"])
def home():
    return render_template("home.html")


@app.route('/data', methods = ["GET"])
def data():
    return render_template("data.html", categories=categories, google_key=GOOGLE_KEY)


@app.route('/results', methods = ["POST"])
def results():
    data = preprocess_data(dict(request.form))

    # Getting the required and optional locations based on data
    required, optional = get_attractions_user_input(data)

    # Call to optimized routing
    optimized_route_output, travel_time, visit_time, num_sites = router(required, optional, data['ranking_considered'] == "yes", data['transport'], int(data['numDays']))

    return render_template("results.html", 
                        routes=optimized_route_output,
                        travel_time=travel_time,
                        visit_time=visit_time,
                        num_sites=num_sites,
                        required=required,
                        optional=optional,
                        google_key=GOOGLE_KEY,
                        transport=data['transport'],
                        )

@app.route('/eval', methods = ["POST"])
def evaluation():
    data = preprocess_data(dict(request.form))

    required, optional = get_attractions_user_input(data)
    print(f"Num required: {len(required)}, Num optional: {len(optional)}")

    for day in [1, 3, 5, 7, 10]:
        for transport in ["public transport", "car", "walking", "bike"]:
            optimized_route_output, travel_time, visit_time, num_sites = router(required, optional, False, transport, day)
            print(f"{day} Days ({transport}):\n {optimized_route_output =}\n {travel_time =}\n {visit_time =}\n {num_sites =}\n")

    return redirect(url_for("data", _method="GET"))          


@app.route('/scrape/<string:city_name>', methods = ["GET"])
def scrape(city_name):
    # CHANGE TO GET if you want to use this!
    try:
        info = update_city(city_name)
        print(info)
    except:
        print("ERROR in scraping")
    
    return redirect(url_for('home', _method="GET"))


@app.route('/<path:other_path>', methods=['GET', 'POST'])
def catch_all(other_path):
	return render_template('404.html', error = "This route doesn't exist")


if __name__ == '__main__':
	app.run(debug = True, port=8081)