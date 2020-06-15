#import numpy as np
from pathlib import Path
import os
from os.path import basename, splitext

#from operator import itemgetter
#from materials import Facet, Model
#from geometry import SpherePoint
#
#

import sys
from models import WavefrontModel
from visualization import plot_function_triangles as plot

if __name__ == "__main__":

    path = sys.argv[1]
    objname = splitext(basename(path))[0]

    model = WavefrontModel.from_path(path)

    def func(viewer_direction):
        return model.total_scatter(viewer_direction)

    filename = objname + ".html"
    plot(func, filename)
