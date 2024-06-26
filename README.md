# travel-optimizer

## Running the website

- Start a Python enviroment
  1. Install venv if you don't have it already: `pip3 install virtualenv`
  2. Create a new environment if one doesn't exist: `python -m venv env`
  3. Activate it: `source env/bin/activate`
- If it's your first time running the program:
  - Download the requirements for the code: `pip3 install -r requirements.txt`
  - Create a configuration file for the secret keys called config.py and add the necessary keys (update if changed):
    - SECRET_KEY="<KEY>"
  - Create a .gitignore file (if it doesn't exist) and add two lines to it:
    - env/
    - config.py
    - .env
  - Create a .env file:
    - GOOGLE_MAPS_API_KEY="<KEY>"
- Start the website: `python3 app.py`
- Open the website (hosted locally). The link should be http://127.0.0.1:5000 or http://localhost:5000. The terminal will tell you which one it is.
- If you make any change, it will be reflected on the website when you refresh the page. If you made a change in the CSS or JS code, it might not be reflected immediately because of cookies and caching; you'll have to do a hard refresh of the page or open it from another browser to see the changes.

## Database
- The preprocessed dataset is [travel.db](/Databases/travel.db)
- You can restart the database anytime by deleting [travel.db](/Databases/travel.db) and reruning the [create-databases.py](/Databases/create-databases.py)
- We recommend using `SQLite` and `SQLite Viewer` extensions in `VSCode` to view and interact with the database.
- To modify any scraping, cleaning or filtering refer to [data_scraper.py](/data_scraper.py) and `get_routes_simple()` function.

## Sidenotes:

1. If you make a change to the configurations, please add the generic name of the variable above.
2. If any major change is made please update the README.
3. If you pip install any packages that everyone should have, make sure only relevant stuff is downloaded (AND everything currently in the [requirements.txt](/requirements.txt) file) and then run `pip freeze > requirements.txt` to reflect the changes for everyone.

## Assumptions:
- Users spend average time given the categories of the place in each location
- We do not account for multiple opening close times throughout the day
- For now, we are only suggesting up to 20 places to the user as optional.
- No flights between locations


