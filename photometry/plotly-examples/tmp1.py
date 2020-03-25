import numpy as np

xs = list(range(5))
ys = list(range(7,13))

mxs, mys = np.meshgrid(xs, ys)
print(mxs)
print(mys)
