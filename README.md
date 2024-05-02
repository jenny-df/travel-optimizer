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
- Start the website: `python3 app.py`
- Open the website (hosted locally). The link should be http://127.0.0.1:5000 or http://localhost:5000. The terminal will tell you which one it is.
- If you make any change, it will be reflected on the website when you refresh the page. If you made a change in the CSS or JS code, it might not be reflected immediately because of cookies and cashing; you'll have to do a hard refresh of the page or open it from another browser to see the changes.
