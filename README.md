# Citrine Coding Challenge

This API is used to as a unit conversion end point. It accepts unit inputs from URL parameters via HTTP get request. The API returns the units converted to there si counter parts.


# How to run
- Open terminal and navigate to folder

- On Mac OS install virtualenv
  'sudo pip install virtualenv'

- For ubuntu
  'sudo apt-get install python-virtualenv'

- Create a virtual environment
  'virtualenv venv'

- Activate virtualenv
 'source venv/bin/activate'

- Install flask
  'pip install flask'

- Export Flask application
    'export FLASK_APP=application.py'
    'export FALSK_DEBUG=1' <!--optional-->

- Run Flask server
    'python application.py'

- Application runs on localhost:5000
- Endpoint http://localhost:5000/units/si

# files
- API is found in application.py
- module functions are found in unit_utils.py
- __init__.py needed for module imports


# inline tests
- in terminal a few tests cases will print

- Written at the bottom of unit_utils
