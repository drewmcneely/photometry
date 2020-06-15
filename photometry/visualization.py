'''
photometry.py. Visualize the photometric output of a Wavefront obj. model.
Copyright (C) 2020  Drew Allen McNeely

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''

import plotly.offline as po
import plotly.express as px
import plotly.graph_objs as go
import numpy as np           
from geometry import IcoSphere, Rotation
import pandas as pd

import progressbar as pb

R = Rotation.for_icosphere()
sphere = IcoSphere.icosahedron().divided(4)

def plot_function_triangles(f, filename):
    #for t in range(5,10):
    #sphere = IcoSphere.icosahedron().divided().reduced(t)
    geo = sphere.geojson
    vals = sphere.mapf(f)
    ids = range(len(vals))
    dat = {'ids':ids, 'vals':vals}
    df = pd.DataFrame(data=dat)

    fig = px.choropleth(df,
        geojson=geo,
        locations='ids',
        color='vals',
        color_continuous_scale="Viridis",
        )

    fig.data[0].marker.line.width = 0
    configure_fig(fig)

    po.plot(fig, filename=filename)

def plot_function_points(f):
    lats = sphere.bary_lats
    lons = sphere.bary_lons
    print("hello")
    vals = sphere.mapf(f)

    fig = px.scatter_geo(lat=lats, lon=lons, color=vals,)

    configure_fig(fig)

    po.plot(fig, filename="points.html")

def plot_sphere_points():
    fig = px.scatter_geo(lat=lats, lon=lons)
    po.plot(fig, filename="points.html")

def configure_fig(fig):
    fig.update_geos(
        visible=False,
        projection=dict(
            type="mollweide",
            rotation=dict(
                lon=.5,
                lat=.5,
                roll=0)),
        lataxis_showgrid=True,
        lonaxis_showgrid=True,
        )

    projections = [
            "mollweide",
            "orthographic",
            "stereographic",
            "equirectangular",
            "mercator",
            "azimuthal equal area",
            "azimuthal equidistant",
            "conic equal area",
            "conic conformal",
            "conic equidistant",
            "gnomonic",
            ]

    buttons = [ dict( args=['geo.projection.type', p], label=p, method='relayout' ) for p in projections ]
    annot = list([ dict(
        x=0.1,
        y=0.8,
        text='Projection',
        yanchor='bottom',
        xref='paper',
        xanchor='right',
        showarrow=False
        )])

    fig.update_layout(
        updatemenus=list([ dict(
            x=0.1,
            y=0.8,
            buttons=buttons,
            yanchor='top',
            )]),
        annotations=annot,
        )

    return fig

if __name__ == "__main__":
    """Test this module on a simple function."""
    def f(p): return p.x
    plot_function_triangles(f)
