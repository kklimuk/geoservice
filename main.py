from flask import Flask, request
from werkzeug.wrappers import Response
from functools import wraps
from pymongo import MongoClient

import json
import geojson

from sys import argv

app = Flask(__name__)
db = MongoClient().geoservice


def validate_location(func):
	@wraps(func)
	def inner(*args, **kwargs):
		if request.args.get('latitude') and request.args.get('latitude'):
			try:
				latitude, longitude = float(request.args.get('latitude')), float(request.args.get('longitude'))
				if -90 <= latitude <= 90 and -180 <= longitude <= 180:
					return func(latitude=latitude, longitude=longitude)
				raise ValueError
			except ValueError:
				return { 
					'error': 'Latitude must be between -90 and 90 and longitude must be between -180 and 180.' 
				}, 400
		elif request.args.get('postal'):
			return func(postal=request.args.get('postal'))

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
def get_location_attributes(latitude=None, longitude=None, postal=None):
	geometry = None
	if postal is not None:
		geometry = (db.features.find_one({ 
			'properties.ZCTA5CE10': postal 
		}) or {}).get('geometry');
	else:
		geometry = geojson.Point((longitude, latitude))

	if geometry is None:
		return { 'error': 'Couldn\'t find anything of note!' }, 404

	return [
		result['properties']
		for result in db.features.find({ 
			'geometry': { 
				'$geoIntersects': { 
					'$geometry': geometry
				}
			}
		}, { 'properties': 1 })
	]


@app.route('/location', methods=['POST'])
@jsonify
def add_location_attributes():
	try:
		data = geojson.loads(request.get_data())
		if isinstance(data, geojson.FeatureCollection):
			return [
				dict(data['features'][i], id=str(oid), _id=str(oid))
				for i, oid in enumerate(db.features.insert(data.features, w=1))
			]
		elif isinstance(data, geojson.Feature):
			oid = db.features.save(data, w=1)
			return dict(data, id=str(oid), _id=str(oid))

		raise Exception('The new location must be a GeoJSON Feature or FeatureCollection.')
	except Exception, e:
		return {
			'error': str(e)
		}, 400


if __name__ == '__main__':
	app.run("0.0.0.0", port=5000)
