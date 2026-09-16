import Rhino as R
import Rhino.Geometry as rg
import System
import rhinoscriptsyntax as rs
from System.Collections.Generic import List
tol=0.001
def geom(x):
    if hasattr(x,'Value'):x=x.Value
    if isinstance(x,System.Guid):x=rs.coercegeometry(x)
    return x
b=geom(Loft)
if isinstance(b,rg.Surface):b=b.ToBrep()
b=b.DuplicateBrep()
face=b.Faces[0]
cutters=[]
for value in Holes:
    c=geom(value)
    # Replace SquishBack's tiny polyline segments with one smooth periodic curve.
    points=[c.PointAt(t) for t in c.DivideByCount(80,True)][:-1]
    uvpoints=[]
    for point in points:
        ok,u,v=face.ClosestPoint(point)
        if not ok:raise ValueError('A hole point could not map to the Loft.')
        uvpoints.append(rg.Point2d(u,v))
    smooth=face.InterpolatedCurveOnSurfaceUV(uvpoints,tol,True,0)
    if smooth is None or not smooth.IsClosed:
        raise ValueError('A smooth on-surface hole is not closed.')
    cutters.append(smooth)
if not cutters:raise ValueError('No closed holes supplied.')
parts=face.Split(List[rg.Curve](cutters),tol)
if parts is None:raise ValueError('Loft could not be cut by the hole curves.')
pieces=[f.DuplicateFace(False) for f in parts.Faces]
pieces.sort(key=lambda f:rg.AreaMassProperties.Compute(f).Area,reverse=True)
Perforated=pieces[0]
if len(pieces)!=len(cutters)+1:
    raise ValueError('Not every hole split the Loft: {} holes, {} regions.'.format(len(cutters),len(pieces)))
# Loft is the inside wall. Force normals away from the ring axis before offsetting.
f=Perforated.Faces[0]
u=f.Domain(0).Mid;v=f.Domain(1).Mid
p=f.PointAt(u,v);n=f.NormalAt(u,v)
center=b.GetBoundingBox(True).Center
if n.X*(p.X-center.X)+n.Y*(p.Y-center.Y)<0:Perforated.Flip()
Solid=rg.Brep.CreateFromOffsetFace(Perforated.Faces[0],float(Thickness),tol,False,True)
if Solid is None or not Solid.IsValid or not Solid.IsSolid:
    raise ValueError('Offset did not produce one valid closed solid. Reduce thickness or simplify holes.')
if Solid.SolidOrientation==rg.BrepSolidOrientation.Inward:Solid.Flip()
mp=rg.MeshingParameters()
mp.Tolerance=0.015
mp.MinimumEdgeLength=0.03
mp.MaximumEdgeLength=0.7
mp.RefineGrid=True
mp.JaggedSeams=False
PrintMesh=rg.Mesh()
for m in rg.Mesh.CreateFromBrep(Solid,mp):PrintMesh.Append(m)
PrintMesh.Vertices.CombineIdentical(True,True)
PrintMesh.Weld(System.Math.PI)
PrintMesh.UnifyNormals()
PrintMesh.Normals.ComputeNormals()
PrintMesh.Compact()
if not PrintMesh.IsValid or not PrintMesh.IsClosed:
    raise ValueError('The export mesh is not closed. Do not print this result.')
volume=rg.VolumeMassProperties.Compute(Solid).Volume
Report='CLOSED SOLID | {} through-holes | thickness {:.2f} mm | volume {:.1f} mm3 | closed print mesh'.format(len(cutters),float(Thickness),volume)
ghenv.Component.Message='CLOSED SOLID | {} holes'.format(len(cutters))
