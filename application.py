"""Unit conversion API.


API receives units from GET Query params and returns conversion to SI units.
"""
from flask import Flask, request, jsonify, abort
import os
import sys
sp = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(sp))
import unit_utils

app = Flask(__name__)


# API Get endpoint by default only accepts HTTP:GET
@app.route('/units/si')
def get_si_unit_object():
    """Endpoint returns si unit conversion as JSON.

    :url_param units: Key-value with 'units' key and values to be converted.
    :returns: Dictionary {"unit_name": <SI-units-converted>,
                          "multiplication_factor": <factor-to-convert-to-SI>}
    :raises: Invalid input type
    """

    # Get none SI units from query parameters
    none_si_units, error = None, None
    try:
        none_si_units = request.args['units'].encode('utf-8')
    except:
        error = "Invalid Query parameter"
        abort(400, {'status': 400, 'error': error})

    # Remove spaces from string and convert to lower case
    none_si_units = none_si_units.replace(" ", "").lower()

    # Check valid units input
    is_valid_input = unit_utils.check_valid_units_string(none_si_units)
    if is_valid_input:
        response = unit_utils.convert_to_si(none_si_units)
        if error in response:
            abort(400, response)
        else:
            return jsonify(response)
    else:
        error = "Invalid Query parameter"
        abort(400, {'status': 400, 'error': error})


if __name__ == '__main__':
    app.run(debug=True)
