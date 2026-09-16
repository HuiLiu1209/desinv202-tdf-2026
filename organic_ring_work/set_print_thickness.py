import Grasshopper as G
import Rhino as R
import System, json, traceback
ROOT='/Users/huiliu/UCB/26Fall/TDF/organic_ring_work/'
d=G.Instances.ActiveCanvas.Document
r={}
def find(g):return d.FindObject(System.Guid(g),False)
def row(o):
    return {'name':o.NickName,'id':str(o.InstanceGuid),'locked':o.Locked,'phase':str(o.Phase),'counts':[p.VolatileDataCount for p in o.Params.Output],'inputs':[{'name':p.Name,'value':str(getattr(o,'CurrentValue','')),'sources':[s.NickName for s in p.Sources]} for p in o.Params.Input],'errors':list(o.RuntimeMessages(G.Kernel.GH_RuntimeMessageLevel.Error)),'warnings':list(o.RuntimeMessages(G.Kernel.GH_RuntimeMessageLevel.Warning))}
try:
    d.Enabled=True
    thickness=find('ed6b38da-047c-4e3b-826a-a019f917f807')
    thickness.NickName='MIN WALL THICKNESS mm'
    thickness.Slider.Minimum=System.Decimal(3.175)
    thickness.Slider.Maximum=System.Decimal(6.35)
    thickness.Slider.DecimalPlaces=3
    # Use extra offset so the finished rounded mesh retains at least 3.175 mm locally.
    thickness.SetSliderValue(System.Decimal(4.5))
    r['set_value']=float(thickness.CurrentValue)
    d.NewSolution(True)
    for g in ['49e8e1f5-36f7-465f-9d52-6c9bafccdce7','91b36d8a-9eb2-417e-b5de-244238020968','9777a8d8-33dd-4968-8f5d-5365c5f7161d']:
        o=find(g);r[o.NickName]=row(o)
        for p in o.Params.Output:
            for x in p.VolatileData.AllData(True):
                v=getattr(x,'Value',None)
                if isinstance(v,R.Geometry.Brep):r[o.NickName+'_'+p.Name]={'valid':v.IsValid,'solid':v.IsSolid,'faces':v.Faces.Count,'edges':v.Edges.Count,'bbox':str(v.GetBoundingBox(True))}
                if isinstance(v,R.Geometry.Mesh):r[o.NickName+'_'+p.Name]={'valid':v.IsValid,'closed':v.IsClosed,'pieces':len(v.SplitDisjointPieces()),'faces':v.Faces.Count,'vertices':v.Vertices.Count,'bbox':str(v.GetBoundingBox(True))}
    r['notes']='Set minimum wall thickness to 3.175 mm. If this result is valid, the downstream round mesh is rebuilt from the thicker solid.'
except:r['error']=traceback.format_exc()
with open(ROOT+'thickness_result.json','w') as f:json.dump(r,f,indent=2)
print('Print thickness set and solution recomputed.')
