import plotly.offline as py
import numpy as np           
from helpers import *
from geometry import SpherePoint, Angle
import pandas as pd

np.set_printoptions(suppress=True,linewidth=80,threshold=80)

class PlotlyStuff:
    # Set the plot layout:
    xaxis=dict(
        showbackground=False,
        showgrid=False,
        showline=True,
        showticklabels=False,
        ticks='',
        title='x',
        zeroline=False
        )
    yaxis=dict(
        showbackground=False,
        showgrid=False,
        showline=True,
        showticklabels=False,
        ticks='',
        title='y',
        zeroline=False
        )
    zaxis=dict(
        showbackground=False,
        showgrid=False,
        showline=True,
        showticklabels=False,
        ticks='',
        title='z',
        zeroline=False
        )

    aspectratio=dict(x=1,y=1,z=1)
    eye=dict(x=1.15, y=1.15, z=1.15)
    camera=dict(eye=eye)
    font=dict(family='Balto', size=14)

    scene=dict(
        xaxis=xaxis, 
        yaxis=yaxis, 
        zaxis=zaxis,
        aspectratio=aspectratio,
        camera=camera
    )

    layout=dict(
        title='Outgoing Longwave Radiation Anomalies<br>Dec 2017-Jan 2018',
        font=font,
        width=800, 
        height=800,
        scene=scene,
        paper_bgcolor='rgba(235,235,235, 0.9)'  
        )

    def sphere(xs, ys, zs, vals, lats, lons):
        nrows, ncolumns = lons.shape

        colorscale=[[0.0, '#313695'],
            [0.07692307692307693, '#3a67af'],
            [0.15384615384615385, '#5994c5'],
            [0.23076923076923078, '#84bbd8'],
            [0.3076923076923077, '#afdbea'],
            [0.38461538461538464, '#d8eff5'],
            [0.46153846153846156, '#d6ffe1'],
            [0.5384615384615384, '#fef4ac'],
            [0.6153846153846154, '#fed987'],
            [0.6923076923076923, '#fdb264'],
            [0.7692307692307693, '#f78249'],
            [0.8461538461538461, '#e75435'],
            [0.9230769230769231, '#cc2727'],
            [1.0, '#a50026']]

        colorbar=dict(thickness=20, len=0.75, ticklen=4, title= 'W/m²')

        # Define the text to be displayed on hover:
        hovertext = [
            ['lon: ' +
                '{:.2f}'.format(lons[i,j]) +
                '<br>lat: ' +
                '{:.2f}'.format(lats[i, j])+
                '<br>W: ' +
                '{:.2f}'.format(vals[i][j])
                for j in range(ncolumns)]
            for i in range(nrows)]

        return dict(
            type='surface',
            x=xs, 
            y=ys, 
            z=zs,
            colorscale=colorscale,
            surfacecolor=vals,
            cmin=-1, 
            cmax=1,
            colorbar=colorbar,
            text=hovertext,
            hoverinfo='text'
            )

def plot(f):
    """f is a function that takes a SpherePoint and returns a value.
    """

    longitudes = Angle.from_degrees(np.arange(0, 360, 10))
    latitudes = Angle.from_degrees(np.arange(-90, 90, 5))
    lats, lons = np.meshgrid(latitudes, longitudes)
    #longitudes = longitudes.tolist()
    #latitudes = latitudes.tolist()

    # In the following functions, f :: lat -> lon -> R

    #def map_mesh(f, lats, lons):
    #    """Map the output of f to the lat/long meshgrid"""
    #    return [
    #        [f(lat, lon) for (lat, lon) in zip(latls, lonls)]
    #        for (latls, lonls) in zip(lats, lons)
    #        ]

    map_mesh = np.vectorize

    to_points = map_mesh(SpherePoint.from_latlon)
    points = to_points(lats, lons)

    xs = map_mesh(lambda p : p.x)(points)
    ys = map_mesh(lambda p : p.y)(points)
    zs = map_mesh(lambda p : p.z)(points)

    vals = map_mesh(f)(points)

    fig=dict(
        data=PlotlyStuff.sphere(xs, ys, zs, vals, lats, lons),
        layout=PlotlyStuff.layout
        )

    filename = f.__name__ + ".html"
    py.plot(fig, filename=filename)

# In order to plot the scalar field  as a heatmap onto the sphere,
# we  define the sphere as a surface colored according   to the `olr` values.
# To ensure  color continuity we extend the `lon` list with [180]
# (its last value was lon[-1]=177.5).
# In this way we can identify lon=-180 with lon=180.
#clons=np.array(lon.tolist()+[180], dtype=np.float64)
#clats=np.array(lat, dtype=np.float64)
#mlons, mlats=np.meshgrid(clons, clats)
#
# Map the meshgrids `mlons`, `mlats` onto the sphere:
#XS, YS, ZS=mapping_map_to_sphere(mlons, mlats)

#print(ZS.shape)

# The sphere points are colormapped according to the values of the numpy array,
# `OLR`, that extends the array `olr`, to ensure color continuity:
#nrows, ncolumns=mlons.shape
#OLR=np.zeros(mlons.shape, dtype=np.float64)
#OLR[:, :ncolumns-1]=np.copy(np.array(olr,  dtype=np.float64))
#OLR[:, ncolumns-1]=np.copy(olr[:, 0])
#
