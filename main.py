from flask import Flask, request
from werkzeug.wrappers import Response
from functools import wraps

import json

app = Flask(__name__)

def validate_location(func):
	@wraps(func)
	def inner(*args, **kwargs):
		try:
			latitude, longitude = float(request.args.get('latitude')), float(request.args.get('longitude'))
			if -180 <= latitude <= 180 and -180 <= longitude <= 180:
				return func(latitude, longitude)
			raise ValueError
		except ValueError:
			return { 
				'error': 'Both latitude and longitude must be numbers between -180 and 180.' 
			}, 400
		except TypeError:
			return {
				'error': 'Both latitude and longitude must be query parameters.'
			}, 400

	return inner

def jsonify(func):
	@wraps(func)
	def inner(*args, **kwargs):
		response = func(*args, **kwargs)
		if not isinstance(response, Response):
			if isinstance(response, tuple):
				response = Response(*response)
			else:
				response = Response(response)
		response.set_data(json.dumps(response.response))

		return response
	return inner

@app.route('/location', methods=['GET'])
@jsonify
@validate_location
def get_location_attributes(latitude, longitude):
	return { 'latitude': latitude, 'longitude': longitude }

@app.route('/location', methods=['POST'])
def add_location_attributes():
	return '', 200

if __name__ == '__main__':
	app.run(debug=True)