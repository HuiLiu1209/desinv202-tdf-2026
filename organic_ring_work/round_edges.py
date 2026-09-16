import Rhino.Geometry as rg
import System
import rhinoscriptsyntax as rs
from System.Collections.Generic import List
if hasattr(Brep,'Value'):Brep=Brep.Value
if isinstance(Brep,System.Guid):Brep=rs.coercebrep(Brep)
radius=float(Radius)
indices=[e.EdgeIndex for e in Brep.Edges if len(set(e.AdjacentFaces()))==2 and not e.IsSmoothManifoldEdge(System.Math.PI/90.0)]
radii=List[System.Double]([radius]*len(indices))
result=rg.Brep.CreateFilletEdges(Brep,List[System.Int32](indices),radii,radii,rg.BlendType.Fillet,rg.RailType.RollingBall,True,0.001,System.Math.PI/180.0)
valid=[b for b in result if b is not None and b.IsValid and b.IsSolid] if result else []
if len(valid)!=1:raise ValueError('Full edge rounding failed at this radius. The sharp solid is not exported.')
Rounded=valid[0]
remaining=[e.EdgeIndex for e in Rounded.Edges if len(set(e.AdjacentFaces()))==2 and not e.IsSmoothManifoldEdge(System.Math.PI/36.0)]
if remaining:raise ValueError('{} sharp edges remain after filleting.'.format(len(remaining)))
mp=rg.MeshingParameters();mp.Tolerance=0.01;mp.MinimumEdgeLength=0.015;mp.MaximumEdgeLength=0.4;mp.RefineGrid=True;mp.JaggedSeams=False
PrintMesh=rg.Mesh()
for m in rg.Mesh.CreateFromBrep(Rounded,mp):PrintMesh.Append(m)
PrintMesh.Vertices.CombineIdentical(True,True);PrintMesh.Weld(System.Math.PI);PrintMesh.UnifyNormals();PrintMesh.Normals.ComputeNormals();PrintMesh.Compact()
if not PrintMesh.IsValid or not PrintMesh.IsClosed:raise ValueError('Rounded print mesh is not watertight.')
Report='ALL EDGES ROUNDED | radius {:.2f} mm | closed solid and watertight mesh'.format(radius)
ghenv.Component.Message='All edges R{:.2f}'.format(radius)
