import plotly.offline as py
import numpy as np           
from scipy.io import netcdf  
import warnings
from helpers import *

np.set_printoptions(suppress=True,linewidth=80,threshold=80)

class PlotlyStuff:
    # Set the plot layout:
    noaxis=dict(
        showbackground=False,
        showgrid=False,
        showline=False,
        showticklabels=False,
        ticks='',
        title='',
        zeroline=False
        )

    aspectratio=dict(x=1,y=1,z=1)
    eye=dict(x=1.15, y=1.15, z=1.15)
    camera=dict(eye=eye)
    font=dict(family='Balto', size=14)

    scene=dict(
        xaxis=noaxis, 
        yaxis=noaxis, 
        zaxis=noaxis,
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

    def sphere(xs, ys, zs, olr, clons, clats, ncolumns, nrows):

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
                '{:.2f}'.format(clons[i,j]) +
                '<br>lat: ' +
                '{:.2f}'.format(clats[i, j])+
                '<br>W: ' +
                '{:.2f}'.format(olr[i][j])
                for j in range(ncolumns)]
            for i in range(nrows)]

        return dict(
            type='surface',
            x=xs, 
            y=ys, 
            z=zs,
            colorscale=colorscale,
            surfacecolor=olr,
            cmin=-20, 
            cmax=20,
            colorbar=colorbar,
            text=hovertext,
            hoverinfo='text'
            )

# Read data from a `netCDF` file:
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    with netcdf.netcdf_file('compday.KsNOdsJTz1.nc', 'r') as f:
        lon = f.variables['lon'][::]       # copy longitude as list
        lat = f.variables['lat'][::-1]     # invert the latitude vector -> South to North
        olr = f.variables['olr'][0,::-1,:] # olr= outgoing longwave radiation
    f.fp   

def data_shift(lon, olr):
    # Shift 'lon' from [0,360] to [-180,180]
    # Correspondingly, shift the olr array
    tmp_lon = np.array([lon[n]-360 if l>=180 else lon[n] 
                       for n,l in enumerate(lon)])  # => [0,180]U[-180,2.5]

    i_east, = np.where(tmp_lon>=0)  # indices of east lon
    i_west, = np.where(tmp_lon<0)   # indices of west lon
    lon = np.hstack((tmp_lon[i_west], tmp_lon[i_east]))  # stack the 2 halves

    olr_ground = np.array(olr)
    olr = np.hstack((olr_ground[:,i_west], olr_ground[:,i_east]))

    return lon, olr

lon, olr = data_shift(lon, olr)

# In order to plot the scalar field  as a heatmap onto the sphere,
# we  define the sphere as a surface colored according   to the `olr` values.
# To ensure  color continuity we extend the `lon` list with [180]
# (its last value was lon[-1]=177.5).
# In this way we can identify lon=-180 with lon=180.
clons=np.array(lon.tolist()+[180], dtype=np.float64)
clats=np.array(lat, dtype=np.float64)
clons, clats=np.meshgrid(clons, clats)


# Map the meshgrids `clons`, `clats` onto the sphere:
XS, YS, ZS=mapping_map_to_sphere(clons, clats)


# The sphere points are colormapped according to the values of the numpy array,
# `OLR`, that extends the array `olr`, to ensure color continuity:
nrows, ncolumns=clons.shape
OLR=np.zeros(clons.shape, dtype=np.float64)
OLR[:, :ncolumns-1]=np.copy(np.array(olr,  dtype=np.float64))
OLR[:, ncolumns-1]=np.copy(olr[:, 0])


fig=dict(
    data=PlotlyStuff.sphere(XS, YS, ZS, OLR, clons, clats, ncolumns, nrows), 
    layout=PlotlyStuff.layout
    )

py.plot(fig, filename="heatmap.html")
