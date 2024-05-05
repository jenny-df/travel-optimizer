from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__,
	template_folder='templates', 
	static_folder='static'
)


app.config.from_pyfile('config.py')


@app.route('/', methods = ["GET"])
def home():
    return render_template("home.html")


@app.route('/data', methods = ["GET"])
def data():
    google_key = "AIzaSyATeWwg3KcuetRkm1nV3xuOGAAZ6uXJNIU"
    return render_template("data.html", google_key=google_key)


@app.route('/results', methods = ["POST"])
def results():
    # Getting values from the form
    data = dict(request.form)
    del data['Submit']
    data['locations'] = data['locations'].split('\n')

	# <TODO> Call to classifier 
    clustering_output = [["1.1", "1.2", "1.3"], ["2.1", "2.2"], ["3.1"]]
    # <TODO> Call to optimized routing
    optimized_route_output = [["1.1", "2.1", "3.1", "2.2"], ["1.2", "1.3"]]

    return render_template("results.html", 
                        clusters = clustering_output, 
                        routes = optimized_route_output
                        )


@app.route('/<path:other_path>', methods=['GET', 'POST'])
def catch_all(other_path):
	return render_template('404.html', error = "This route doesn't exist")


if __name__ == '__main__':
	app.secret_key = 'sjkdfh239G$FJLD239#89QEFAS239DFJISALFJ!$'
	app.run(debug = True)