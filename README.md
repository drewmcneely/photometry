# photometry.py

This is a collection of routines to model the reflectivity and visualize the photometric output of an illuminated space object.
The project imports Wavefront .obj files and generates a crude "convex" approximation of the data.
So far, only visualizing the photometric output is implemented.
Visualization is generated using plotly and writes to an html file taking the same name as the input .obj file.

## Getting Started

As of now, it is sufficient to run the script as-is without installation or setup.
From the root directory, navigate into photometry/photometry/ and run `python3 photometry.py <filename>` where <filename> is a Wavefront .obj file.
An example `cube.obj` has been provided.

### Prerequisites

This software depends on Python packages including numpy, scipy, pymesh, plotly, and progressbar2. These packages can be installed through pip.

## Authors

* **Drew Allen McNeely**

## License

This project is licensed under the GNU GPL v2.0 - see the [LICENSE.txt](LICENSE.txt) file for details
