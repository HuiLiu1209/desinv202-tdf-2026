import Rhino.Geometry as rg
import System
import rhinoscriptsyntax as rs

def geom(x):
    if hasattr(x, 'Value'): x = x.Value
    if isinstance(x, System.Guid): x = rs.coercebrep(x)
    if isinstance(x, rg.Surface): x = x.ToBrep()
    return x

b = geom(U)
if b is None: raise ValueError('Connect the existing squished UVSurface.')
Boundary = list(rg.Curve.JoinCurves(b.DuplicateNakedEdgeCurves(True, False), 0.001))
box = b.GetBoundingBox(True)
box.Inflate(1.0)
Bounds = rg.Rectangle3d(rg.Plane.WorldXY, rg.Interval(box.Min.X, box.Max.X), rg.Interval(box.Min.Y, box.Max.Y))
ghenv.Component.Message = 'Actual UV outline'
