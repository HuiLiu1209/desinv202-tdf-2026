import Grasshopper as G,Rhino as R,System,json,traceback,time
ROOT='/Users/huiliu/UCB/26Fall/TDF/organic_ring_work/'
d=G.Instances.ActiveCanvas.Document
r={}
try:
 d.Enabled=True
 solid=d.FindObject(System.Guid('91b36d8a-9eb2-417e-b5de-244238020968'),False)
 rounding=d.FindObject(System.Guid('9777a8d8-33dd-4968-8f5d-5365c5f7161d'),False)
 rounding.Code=open(ROOT+'round_edges.py').read()
 rounding.ExpireSolution(False)
 d.NewSolution(False)
 for guid in ['91b36d8a-9eb2-417e-b5de-244238020968','9777a8d8-33dd-4968-8f5d-5365c5f7161d']:
  o=d.FindObject(System.Guid(guid),False)
  row={'counts':[p.VolatileDataCount for p in o.Params.Output],'errors':list(o.RuntimeMessages(G.Kernel.GH_RuntimeMessageLevel.Error)),'warnings':list(o.RuntimeMessages(G.Kernel.GH_RuntimeMessageLevel.Warning))}
  for p in o.Params.Output:
   for x in p.VolatileData.AllData(True):
    if hasattr(x,'Value') and isinstance(x.Value,R.Geometry.Brep):row[p.Name]={'edges':x.Value.Edges.Count,'faces':x.Value.Faces.Count,'solid':x.Value.IsSolid}
  r[o.NickName]=row
 G.Instances.ActiveCanvas.Refresh();R.RhinoDoc.ActiveDoc.Views.Redraw()
except:r['error']=traceback.format_exc()
with open(ROOT+'refine_result.json','w') as f:json.dump(r,f,indent=2)
print('Smooth edge structure tested.')
