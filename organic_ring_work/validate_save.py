import Rhino as R
import Grasshopper as G
import clr
clr.AddReference('GH_IO')
import GH_IO
import System
import System.Drawing as D
import scriptcontext as sc
import json,traceback
ROOT='/Users/huiliu/UCB/26Fall/TDF/'
doc=G.Instances.ActiveCanvas.Document
r={}
try:
    def find(g):return doc.FindObject(System.Guid(g),False)
    def values(p):return [x.Value for x in p.VolatileData.AllData(True)]
    clip=find('034aada3-b665-419b-a4a8-348e8499b68e')
    mapper=find('ad095307-9c63-4711-a6e7-206f2a684495')
    U=sc.doc.Objects.FindId(System.Guid('a5f31448-51ea-43f6-8400-f3a7a429b2b2')).Geometry
    T=sc.doc.Objects.FindId(System.Guid('9f4b7a84-0df9-431b-9b62-1de7d7929990')).Geometry
    cells=values(clip.Params.Output[0])
    mapped=values(mapper.Params.Output[1])
    holes=values(mapper.Params.Output[2])
    r['uv_area_mm2']=R.Geometry.AreaMassProperties.Compute(U).Area
    r['cells_area_mm2']=sum(R.Geometry.AreaMassProperties.Compute(c).Area for c in cells)
    r['area_relative_error']=abs(r['cells_area_mm2']-r['uv_area_mm2'])/r['uv_area_mm2']
    for name,curves in [('voronoi',mapped),('rounded_holes',holes)]:
        distances=[]
        for c in curves:
            for t in c.DivideByCount(30,True):
                p=c.PointAt(t)
                distances.append(p.DistanceTo(T.ClosestPoint(p)))
        r[name]={'count':len(curves),'closed':sum(c.IsClosed for c in curves),'valid':sum(c.IsValid for c in curves),'max_surface_distance_mm':max(distances)}
    archive=GH_IO.Serialization.GH_Archive()
    archive.AppendObject(doc,'Definition')
    r['gh_saved']=archive.WriteToFile(ROOT+'Organic_Ring_Voronoi.gh',True,False)
    options=R.FileIO.FileWriteOptions()
    r['rhino_saved']=sc.doc.WriteFile(ROOT+'Organic_Ring_Voronoi.3dm',options)
    # Select output for visible preview and focus the Perspective viewport on this model.
    for obj in doc.Objects:obj.Attributes.Selected=False
    find('48ee1d20-201a-44f5-b03e-be7a0392a263').Attributes.Selected=True
    for view in sc.doc.Views:
        if view.ActiveViewport.Name=='Perspective':
            box=T.GetBoundingBox(True);box.Inflate(8)
            view.ActiveViewport.ZoomBoundingBox(box)
    sc.doc.Views.Redraw()
    G.Instances.ActiveCanvas.Refresh()
except:
    r['error']=traceback.format_exc()
with open(ROOT+'organic_ring_work/validation.json','w') as f:json.dump(r,f,indent=2)
print('Organic ring validation and save completed.')
