import Rhino.Geometry as rg
import System,math
import rhinoscriptsyntax as rs
if hasattr(Brep,'Value'):Brep=Brep.Value
if isinstance(Brep,System.Guid):Brep=rs.coercebrep(Brep)
mp=rg.MeshingParameters();mp.Tolerance=0.01;mp.MinimumEdgeLength=0.03;mp.MaximumEdgeLength=0.4;mp.RefineGrid=True;mp.JaggedSeams=False
source=rg.Mesh()
for m in rg.Mesh.CreateFromBrep(Brep,mp):source.Append(m)
source.Vertices.CombineIdentical(True,True);source.Weld(System.Math.PI)
sp=rg.ShrinkWrapParameters()
sp.TargetEdgeLength=0.15
sp.SmoothingIterations=int(Smooth)
sp.Offset=0.0
sp.PolygonOptimization=0
sp.FillHolesInInputObjects=False
sp.InflateVerticesAndPoints=False
PrintMesh=source.ShrinkWrap(sp)
if PrintMesh is None:raise ValueError('Organic edge smoothing failed.')
PrintMesh.Vertices.CombineIdentical(True,True);PrintMesh.Weld(System.Math.PI);PrintMesh.UnifyNormals();PrintMesh.Normals.ComputeNormals();PrintMesh.Compact()
PrintMesh.Faces.ConvertQuadsToTriangles()
if not PrintMesh.IsValid or not PrintMesh.IsClosed or len(PrintMesh.SplitDisjointPieces())!=1:
    raise ValueError('The rounded ring must be one valid closed mesh.')
if rg.VolumeMassProperties.Compute(PrintMesh).Volume<0:
    PrintMesh.Flip(True,True,True)
    PrintMesh.UnifyNormals()
    PrintMesh.Normals.ComputeNormals()
# Minimum distance of mesh edges to the ring axis, in XY. This preserves the bore
# after smoothing, including triangle chords between mesh vertices.
vertices=[(float(p.X),float(p.Y)) for p in PrintMesh.Vertices]
minr2=1e99
for f in PrintMesh.Faces:
    for i,j in [(f.A,f.B),(f.B,f.C),(f.C,f.A)]:
        ax,ay=vertices[i];bx,by=vertices[j];dx=bx-ax;dy=by-ay
        den=dx*dx+dy*dy
        t=max(0.0,min(1.0,-(ax*dx+ay*dy)/den)) if den>1e-20 else 0.0
        qx=ax+t*dx;qy=ay+t*dy
        minr2=min(minr2,qx*qx+qy*qy)
measured=2.0*math.sqrt(minr2)
scale=float(Diameter)/measured
PrintMesh.Transform(rg.Transform.Scale(rg.Plane.WorldXY,scale,scale,1.0))
Rounded=PrintMesh
Report='ORGANIC CLOSED PRINT MESH | bore {:.2f} mm | {} smoothing steps | {} triangles | Loft + Offset linked'.format(float(Diameter),int(Smooth),PrintMesh.Faces.Count)
ghenv.Component.Message='Rounded mesh | ID {:.2f}'.format(float(Diameter))
