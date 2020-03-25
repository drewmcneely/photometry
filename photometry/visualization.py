import plotly.offline as py
import numpy as np           
from geometry import SpherePoint, Angle
import pandas as pd

from urllib.request import urlopen
import json

urlst = 'https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json'
fname = 'geojson-counties-fips.json'

with open(fname) as f:
    counties = json.load(f)

"""
counties = {
    "type" : "FeatureCollection",
    "features" : [A...]
    }

A[0] = {
    "type": "Feature",
    "properties": {
        "GEO_ID": "0500000US01001",
        "STATE": "01",
        "COUNTY": "001",
        "NAME": "Autauga",
        "LSAD": "County",
        "CENSUSAREA": 594.436
        },
    "geometry": {
        "type": "Polygon",
        "coordinates": [[
            [lon1, lat1],
            [lon2, lat2], ...
            ]]
        }
    "id": "01001"
    }



"""


print(counties['features'][0])
