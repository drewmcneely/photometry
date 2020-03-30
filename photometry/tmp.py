import plotly.express as px
import plotly.offline as po
import visualization as vis
from geometry import IcoSphere

def f(p): return p.x

#fig = plot(f)
#po.plot(fig, filename="x_plus_y.html")
sphere = IcoSphere.sphere
vis.plot_sphere_points()
