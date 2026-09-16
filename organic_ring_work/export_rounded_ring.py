import Rhino as R,Grasshopper as G,System,clr,scriptcontext as sc
import System.Drawing as D
import json,struct,traceback,math
clr.AddReference('GH_IO');import GH_IO
ROOT='/Users/huiliu/UCB/26Fall/TDF/'
d=G.Instances.ActiveCanvas.Document
rdoc=R.RhinoDoc.ActiveDoc
r=json.load(open(ROOT+'organic_ring_work/final_print_validation.json'))
r.pop('error',None)
def find(g):return d.FindObject(System.Guid(g),False)
def val(p):return [x.Value for x in p.VolatileData.AllData(True)]
rounder=find('9777a8d8-33dd-4968-8f5d-5365c5f7161d')
diameter=find('287f171f-96cf-432d-8512-7d1bbf1a6c74')
def save_status():
    with open(ROOT+'organic_ring_work/final_print_validation.json','w') as f:json.dump(r,f,indent=2)
try:
    d.Enabled=True
    rounder.Code=open(ROOT+'organic_ring_work/organic_round_mesh.py').read()
    rounder.ExpireSolution(False)
    diameter.SetSliderValue(System.Decimal(22));d.NewSolution(False)
    r['stage']='Verifying restored 22 mm print mesh';save_status()
    m=val(rounder.Params.Output[2])[0].DuplicateMesh();m.Faces.ConvertQuadsToTriangles()
    r['valid']=m.IsValid;r['closed']=m.IsClosed;r['pieces']=len(m.SplitDisjointPieces());r['manifold']=list(m.IsManifold(True));r['triangles']=m.Faces.Count
    r['volume_mm3']=R.Geometry.VolumeMassProperties.Compute(m).Volume
    r['bbox']=str(m.GetBoundingBox(True))
    r['self_intersection_stage']='running';save_status()
    token=getattr(System.Threading.CancellationToken,'None')
    hits=m.GetSelfIntersections(1e-7,True,False,None,token,None)
    r['self_intersection_check_success']=bool(hits[0]);r['self_intersection_curves']=len(hits[1]) if hits[1] is not None else 0;r['overlap_curves']=len(hits[2]) if hits[2] is not None else 0
    r['self_intersection_stage']='complete'
    coords=[(float(p.X),float(p.Y)) for p in m.Vertices];minimum=1e99
    for face in m.Faces:
        for i,j in ((face.A,face.B),(face.B,face.C),(face.C,face.A)):
            ax,ay=coords[i];bx,by=coords[j];dx=bx-ax;dy=by-ay;den=dx*dx+dy*dy
            t=max(0.,min(1.,-(ax*dx+ay*dy)/den)) if den>1e-20 else 0.
            minimum=min(minimum,(ax+t*dx)**2+(ay+t*dy)**2)
    r['measured_inner_diameter_mm']=2*math.sqrt(minimum)
    # Check radial thickness away from rims using inward-facing surface normals.
    thickness=[]
    m.FaceNormals.ComputeFaceNormals()
    stride=max(1,m.Faces.Count//2400)
    for i in range(0,m.Faces.Count,stride):
        p=m.Faces.GetFaceCenter(i);rad=R.Geometry.Vector3d(p.X,p.Y,0);rad.Unitize();n=m.FaceNormals[i]
        if n.X*rad.X+n.Y*rad.Y < -0.985:
            start=p+rad*0.02
            hit=R.Geometry.Intersect.Intersection.MeshRay(m,R.Geometry.Ray3d(start,rad))
            if hit>0:thickness.append(hit+0.02)
    r['sampled_wall_thickness_mm']={'min':min(thickness),'max':max(thickness),'samples':len(thickness)} if thickness else None
    wall=find('ed6b38da-047c-4e3b-826a-a019f917f807')
    r['wall_thickness_param_mm']=float(wall.CurrentValue)
    if r['wall_thickness_param_mm'] < 3.175-1e-6:
        raise ValueError('Wall thickness parameter is below 3.175 mm.')
    if not(r['valid'] and r['closed'] and r['pieces']==1 and r['manifold'][0] and r['manifold'][1] and not r['manifold'][2]):raise ValueError('Mesh topology failed.')
    if not r['self_intersection_check_success'] or r['self_intersection_curves'] or r['overlap_curves']:raise ValueError('Mesh self-intersections detected.')
    r['stage']='Saving verified final artifacts';save_status()
    f3=R.FileIO.File3dm();f3.Settings.ModelUnitSystem=R.UnitSystem.Millimeters
    at=R.DocObjects.ObjectAttributes();at.Name='Organic Ring - ID22 - all edges smoothed';at.ObjectColor=D.Color.FromArgb(205,164,100);at.ColorSource=R.DocObjects.ObjectColorSource.ColorFromObject
    f3.Objects.AddMesh(m,at);r['print_3dm_saved']=f3.Write(ROOT+'Organic_Ring_Print_ID22mm_Wall3p175mm.3dm',8)
    with open(ROOT+'Organic_Ring_Print_ID22mm_Wall3p175mm.stl','wb') as f:
        f.write(b'Organic ring ID22mm | wall 3.175mm | units mm | rounded closed mesh'.ljust(80,b' '));f.write(struct.pack('<I',m.Faces.Count))
        for face in m.Faces:
            p=R.Geometry.Point3d(m.Vertices[face.A]);q=R.Geometry.Point3d(m.Vertices[face.B]);s=R.Geometry.Point3d(m.Vertices[face.C]);n=R.Geometry.Vector3d.CrossProduct(q-p,s-p);n.Unitize()
            f.write(struct.pack('<12fH',n.X,n.Y,n.Z,p.X,p.Y,p.Z,q.X,q.Y,q.Z,s.X,s.Y,s.Z,0))
    # Preserve the live GH output plus an explicitly named Rhino export snapshot.
    layer=R.DocObjects.Layer();layer.Name='PRINT - 22mm rounded snapshot';layer.Color=D.Color.FromArgb(205,164,100)
    at.LayerIndex=rdoc.Layers.Add(layer);at.SetUserString('Source','Organic_Ring_Voronoi.gh / PRINT - Rounded Ring')
    r['rhino_snapshot_id']=str(rdoc.Objects.AddMesh(m,at))
    uv=find('9f9fbb64-896a-4293-8be2-cfa9a4b38141');uv.PersistentData.Clear()
    archive=GH_IO.Serialization.GH_Archive();archive.AppendObject(d,'Definition');r['gh_saved']=archive.WriteToFile(ROOT+'Organic_Ring_Voronoi.gh',True,False)
    r['rhino_project_saved']=rdoc.WriteFile(ROOT+'Organic_Ring_Voronoi.3dm',R.FileIO.FileWriteOptions())
    # Focus the rounded snapshot in a useful three-quarter view.
    rdoc.Objects.UnselectAll()
    for view in rdoc.Views:
        if view.ActiveViewport.Name=='Perspective':
            box=m.GetBoundingBox(True);box.Inflate(2);view.ActiveViewport.ZoomBoundingBox(box)
    rdoc.Views.Redraw();G.Instances.ActiveCanvas.Refresh()
    r['stage']='complete';save_status()
except:
    r['error']=traceback.format_exc();save_status()
