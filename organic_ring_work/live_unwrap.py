import Rhino.Geometry as rg
import System
import rhinoscriptsyntax as rs
if hasattr(Loft,'Value'): Loft=Loft.Value
if isinstance(Loft,System.Guid): Loft=rs.coercebrep(Loft)
if isinstance(Loft,rg.Surface): Loft=Loft.ToBrep()
if Loft is None or Loft.Faces.Count!=1: raise ValueError('Connect the single-face ring Loft.')
sp=rg.SquishParameters()
sp.PreserveTopology=False
sp.SaveMapping=True
with rg.Squisher() as sq:
    UV=sq.SquishSurface(sp,Loft.Faces[0])
if UV is None or not rg.Squisher.Is2dPatternSquished(UV):
    raise ValueError('The current Loft could not be flattened with mapping data.')
# Move the pattern clear of the ring; the saved mapping follows this transform.
UV.Transform(rg.Transform.Translation(-110.0,0.0,0.0))
ghenv.Component.Message='Live from Loft'
