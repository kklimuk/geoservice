# GeoService
In order to import the files into mongodb, first convert them into JSON arrays via:
```
cat geodata/[FILENAME].geojson | python transformer.py > [FILENAME].json
```

Then import them into a database named `geoservice` and the collection `features` via:
```
mongoimport --db geoservice --collection features --file geodata/[FILENAME].json --jsonArray
```

Don't forget to replace [FILENAME] with the name of the geodata you want to transform!