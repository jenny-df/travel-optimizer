from flask import Flask, render_template, request, url_for, redirect
import os
from dotenv import load_dotenv
from data_scraper import *


app = Flask(__name__,
	template_folder='templates', 
	static_folder='static'
)

app.config.from_pyfile('config.py')

load_dotenv()

@app.route('/', methods = ["GET"])
def home():
    return render_template("home.html")


@app.route('/data', methods = ["GET"])
def data():
    # <TODO> Tamar: Get all categories
    categories = ['Parks', 'Casinos', 'Tourist Attractions']
    return render_template("data.html", categories=categories, google_key=os.getenv('GOOGLE_MAPS_API_KEY'))


@app.route('/results', methods = ["POST"])
def results():
    # Getting values from the form
    data = dict(request.form)
    del data['Submit']
    data['must_locations'] = data['must_locations'].split('\r\n')
    data['categories_of_locations'] = request.form.getlist('categories_of_locations')

	# <TODO> Audrey: Call to classifier 
    clustering_output = [["1.1", "1.2", "1.3"], ["2.1", "2.2"], ["3.1"]]
    # <TODO> Audrey: Call to optimized routing
    optimized_route_output = [["1.1", "2.1", "3.1", "2.2"], ["1.2", "1.3"]]

    return render_template("results.html", 
                        clusters = clustering_output, 
                        routes = optimized_route_output
                        )

@app.route('/scrape/<string:city_name>', methods = ["POST"])
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
	app.run(debug = True)