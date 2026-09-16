import Grasshopper as G, Rhino as R, System, json, traceback
from System import DateTime
d=G.Instances.ActiveCanvas.Document
r={}
try:
 r['enabled_before']=G.Kernel.GH_Document.EnableSolutions
 r['doc_enabled']=d.Enabled
 d.Enabled=True
 G.Kernel.GH_Document.EnableSolutions=True
 d.NewSolution(True)
 r['nodes']=[]
 for o in d.Objects:
  if hasattr(o,'Params'):
   r['nodes'].append({'name':o.NickName,'id':str(o.InstanceGuid),'locked':o.Locked,'phase':str(o.Phase),'counts':[p.VolatileDataCount for p in o.Params.Output],'inputs':[{'name':p.Name,'sources':[s.NickName for s in p.Sources],'count':p.VolatileDataCount} for p in o.Params.Input],'errors':list(o.RuntimeMessages(G.Kernel.GH_RuntimeMessageLevel.Error)),'warnings':list(o.RuntimeMessages(G.Kernel.GH_RuntimeMessageLevel.Warning))})
 G.Instances.ActiveCanvas.Refresh()
 R.RhinoDoc.ActiveDoc.Views.Redraw()
except:r['error']=traceback.format_exc()
with open('/Users/huiliu/UCB/26Fall/TDF/organic_ring_work/solid_recompute.json','w') as f:json.dump(r,f,indent=2)
print('Solid solution checked.')
