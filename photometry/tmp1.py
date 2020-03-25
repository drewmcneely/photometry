from collections import deque

ps = deque(["a", "b", "c"])
pr = ps.copy()
pr.rotate(-1)
def midpoint(a,b): return a+b
mids = deque([midpoint(s,r) for s,r in zip(ps, pr)])
midr = mids.copy()
midr.rotate()
def tri(a,b,c): return "%s %s %s"%(a,b,c)
tris = [tri(*z) for z in zip(ps, mids, midr)]
print(tris + [tri(*mids)])
