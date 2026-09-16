import Rhino.Geometry as rg
import Rhino
import System
import rhinoscriptsyntax as rs
from System.Collections.Generic import List

def geom(x):
    if hasattr(x, 'Value'): x = x.Value
    if isinstance(x, System.Guid): x = rs.coercegeometry(x)
    return x

b = geom(U)
if isinstance(b, rg.Surface): b = b.ToBrep()
if not rg.Squisher.Is2dPatternSquished(b):
    raise ValueError('U must retain Squish data. Reference the original Squish surface, not a rebuilt boundary surface.')

def back(items):
    curves = [geom(x) for x in items if x is not None]
    result = rg.Squisher.SquishBack2dMarks(b, List[rg.GeometryBase](curves))
    if result is None: raise ValueError('SquishBack failed. Check the source surface.')
    result = list(result)
    if any(x is None for x in result):
        raise ValueError('A curve could not map. Check that every curve lies inside the UV boundary.')
    return result

Cells3D = back(Cells)
Holes3D = back(Holes)
Report = '{} Voronoi cells + {} rounded hole curves mapped to original model.'.format(len(Cells3D),len(Holes3D))
ghenv.Component.Message = 'SquishBack | {} holes'.format(len(Holes3D))
