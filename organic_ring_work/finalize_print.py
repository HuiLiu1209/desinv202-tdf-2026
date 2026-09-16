import Rhino as R, Grasshopper as G, System, clr, scriptcontext as sc
import System.Drawing as D
import json,traceback,struct,math
clr.AddReference('GH_IO')
import GH_IO
ROOT='/Users/huiliu/UCB/26Fall/TDF/'
d=G.Instances.ActiveCanvas.Document
r={}
def find(g):return d.FindObject(System.Guid(g),False)
def val(p):return [x.Value for x in p.VolatileData.AllData(True)]
solidnode=find('91b36d8a-9eb2-417e-b5de-244238020968')
radius=find('287f171f-96cf-432d-8512-7d1bbf1a6c74')
original=radius.CurrentValue
try:
    d.Enabled=True
    before=val(solidnode.Params.Output[2])[0].GetBoundingBox(True)
    try:
        radius.SetSliderValue(original-System.Decimal(1))
        d.NewSolution(True)
        test=val(solidnode.Params.Output[2])
        r['loft_link_test']={'tested_radius_mm':float(radius.CurrentValue),'closed_solid':bool(test and test[0].IsSolid),'bbox_changed':bool(test and test[0].GetBoundingBox(True).Diagonal.Length!=before.Diagonal.Length)}
    finally:
        radius.SetSliderValue(original)
        d.NewSolution(True)
    solids=val(solidnode.Params.Output[2]);meshes=val(solidnode.Params.Output[3])
    if len(solids)!=1 or len(meshes)!=1:raise ValueError('Expected one solid and one print mesh after restoring Loft.')
    b=solids[0];m=meshes[0].DuplicateMesh()
    m.Faces.ConvertQuadsToTriangles()
    manifold=m.IsManifold(True)
    r['solid']={'valid':b.IsValid,'closed':b.IsSolid,'naked_edges':sum(e.Valence==R.Geometry.EdgeAdjacency.Naked for e in b.Edges),'volume_mm3':R.Geometry.VolumeMassProperties.Compute(b).Volume,'bbox':str(b.GetBoundingBox(True))}
    r['mesh']={'valid':m.IsValid,'closed':m.IsClosed,'connected_pieces':len(m.SplitDisjointPieces()),'manifold':list(manifold),'triangles':m.Faces.Count}
    r['radius_mm']=float(original)
    r['thickness_mm']=float(find('ed6b38da-047c-4e3b-826a-a019f917f807').CurrentValue)
    r['report']=[str(x) for x in solidnode.Params.Output[4].VolatileData.AllData(True)]
    if not b.IsSolid or not b.IsValid or not m.IsClosed or not m.IsValid or len(m.SplitDisjointPieces())!=1 or not manifold[0]:raise ValueError('Print topology validation failed.')
    # Measure actual hole-to-hole and hole-to-rim distances in model space.
    holes=val(find('ad095307-9c63-4711-a6e7-206f2a684495').Params.Output[2])
    loft=val(find('49e8e1f5-36f7-465f-9d52-6c9bafccdce7').Params.Output[0])[0]
    rims=R.Geometry.Curve.JoinCurves(loft.DuplicateNakedEdgeCurves(True,False),0.001)
    webmin=1e9;rimmin=1e9
    for i,c in enumerate(holes):
        for t in c.DivideByCount(80,True):
            p=c.PointAt(t)
            for q in holes[i+1:]:
                ok,s=q.ClosestPoint(p)
                if ok:webmin=min(webmin,p.DistanceTo(q.PointAt(s)))
            for q in rims:
                ok,s=q.ClosestPoint(p)
                if ok:rimmin=min(rimmin,p.DistanceTo(q.PointAt(s)))
    r['sampled_min_hole_gap_mm']=webmin
    r['sampled_min_edge_rim_mm']=rimmin
    # Export a single verified printable object, preserving millimetres in 3DM.
    f3=R.FileIO.File3dm();f3.Settings.ModelUnitSystem=R.UnitSystem.Millimeters
    attr=R.DocObjects.ObjectAttributes();attr.Name='Organic Ring - closed solid, live Loft';f3.Objects.AddBrep(b,attr)
    r['print_3dm_saved']=f3.Write(ROOT+'Organic_Ring_Print.3dm',8)
    with open(ROOT+'Organic_Ring_Print.stl','wb') as f:
        f.write(b'Organic ring | millimetres | live Loft | closed mesh'.ljust(80,b' '));f.write(struct.pack('<I',m.Faces.Count))
        for face in m.Faces:
            a=R.Geometry.Point3d(m.Vertices[face.A]);bb=R.Geometry.Point3d(m.Vertices[face.B]);c=R.Geometry.Point3d(m.Vertices[face.C])
            n=R.Geometry.Vector3d.CrossProduct(bb-a,c-a);n.Unitize()
            f.write(struct.pack('<12fH',n.X,n.Y,n.Z,a.X,a.Y,a.Z,bb.X,bb.Y,bb.Z,c.X,c.Y,c.Z,0))
    # Remove the obsolete stored external surface reference from the now-live UV parameter.
    uv=find('9f9fbb64-896a-4293-8be2-cfa9a4b38141');uv.PersistentData.Clear()
    # Make dimensions and final outputs obvious in the definition.
    radius.NickName='Loft inner radius mm'
    printout=find('dd433037-054a-41b4-a033-bed94328c616')
    printout.NickName='CLOSED PRINTABLE RING'
    for o in d.Objects:
        o.Attributes.Selected=False
        if hasattr(o,'Hidden'):o.Hidden=True
    printout.Hidden=False
    printout.Attributes.Selected=True
    # Save the complete dynamic definition, including embedded Python code.
    a=GH_IO.Serialization.GH_Archive();a.AppendObject(d,'Definition')
    r['gh_saved']=a.WriteToFile(ROOT+'Organic_Ring_Voronoi.gh',True,False)
    r['project_saved']=sc.doc.WriteFile(ROOT+'Organic_Ring_Voronoi.3dm',R.FileIO.FileWriteOptions())
    for view in sc.doc.Views:
        if view.ActiveViewport.Name=='Perspective':
            box=b.GetBoundingBox(True);box.Inflate(4);view.ActiveViewport.ZoomBoundingBox(box)
    sc.doc.Views.Redraw();G.Instances.ActiveCanvas.Refresh()
except:r['error']=traceback.format_exc()
with open(ROOT+'organic_ring_work/print_validation.json','w') as f:json.dump(r,f,indent=2)
print('Print model verification and export completed.')
