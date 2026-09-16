import Rhino as R, Grasshopper as G, System, clr, scriptcontext as sc
import json,traceback,time
r={}
try:
 d=G.Instances.ActiveCanvas.Document
 loft=d.FindObject(System.Guid('49e8e1f5-36f7-465f-9d52-6c9bafccdce7'),False)
 vals=list(loft.Params.Output[0].VolatileData.AllData(True))
 b=vals[0].Value
 r['loft']={'count':len(vals),'bbox':str(b.GetBoundingBox(True)),'faces':b.Faces.Count,'valid':b.IsValid,'area':R.Geometry.AreaMassProperties.Compute(b).Area,'type':str(b.GetType())}
 r['squish_props']=[str(p) for p in clr.GetClrType(R.Geometry.SquishParameters).GetProperties()]
 sp=R.Geometry.SquishParameters()
 sp.PreserveTopology=False
 sq=R.Geometry.Squisher()
 start=time.time()
 flat=sq.SquishSurface(sp,b.Faces[0])
 r['squish']={'seconds':time.time()-start,'bbox':str(flat.GetBoundingBox(True)),'mapping':R.Geometry.Squisher.Is2dPatternSquished(flat),'edges':flat.Edges.Count,'area':R.Geometry.AreaMassProperties.Compute(flat).Area}
 r['canvas_props']=[str(p) for p in G.Instances.ActiveCanvas.Viewport.GetType().GetProperties()]
 r['canvas_methods']=[str(m) for m in G.Instances.ActiveCanvas.GetType().GetMethods() if any(s in m.Name for s in ['Zoom','View','Fit'])]
 r['tol']=sc.doc.ModelAbsoluteTolerance
 r['sliders']=[{'id':str(o.InstanceGuid),'name':o.NickName,'value':str(o.CurrentValue)} for o in d.Objects if hasattr(o,'CurrentValue')]
except:r['error']=traceback.format_exc()
with open('/Users/huiliu/UCB/26Fall/TDF/organic_ring_work/live_probe.json','w') as f:json.dump(r,f,indent=2)
print('Live Loft checked.')
