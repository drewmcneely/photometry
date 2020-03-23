from numpy.linalg import norm

def normalize(v):
    n = norm(v)
    if n==0: return v
    else: return v/n
