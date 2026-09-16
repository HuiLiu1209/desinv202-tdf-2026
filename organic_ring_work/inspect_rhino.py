import Rhino
import scriptcontext as sc
import Grasshopper as gh
import json
import traceback

report = {}
try:
    doc = gh.Instances.ActiveCanvas.Document
    report['units'] = str(sc.doc.ModelUnitSystem)
    report['gh'] = []
    for obj in doc.Objects:
        row = {'id':str(obj.InstanceGuid), 'component':str(obj.ComponentGuid), 'name':obj.Name, 'nick':obj.NickName, 'type':str(obj.GetType()), 'pivot':str(obj.Attributes.Pivot)}
        if hasattr(obj,'PersistentData'):
            row['data'] = []
            for item in obj.PersistentData.AllData(True):
                d = {'text':str(item), 'type':str(item.GetType())}
                if hasattr(item,'ReferenceID'): d['ref'] = str(item.ReferenceID)
                row['data'].append(d)
        if hasattr(obj,'Params'):
            row['inputs'] = [{'name':p.Name,'sources':[str(s.InstanceGuid) for s in p.Sources]} for p in obj.Params.Input]
        report['gh'].append(row)
    report['objects'] = []
    for obj in sc.doc.Objects:
        g = obj.Geometry
        row = {'id':str(obj.Id),'name':obj.Attributes.Name, 'type':str(g.GetType()),'bbox':str(g.GetBoundingBox(True)), 'selected':obj.IsSelected(False), 'user_data':[str(u.GetType()) if u else 'native data' for u in g.UserData]}
        if isinstance(g,Rhino.Geometry.Brep):
            row['faces'] = [{'planar':f.IsPlanar(),'u':str(f.Domain(0)),'v':str(f.Domain(1)), 'surface':str(f.UnderlyingSurface().GetType()),'area':Rhino.Geometry.AreaMassProperties.Compute(f).Area} for f in g.Faces]
        report['objects'].append(row)
    report['proxies'] = []
    for p in gh.Instances.ComponentServer.ObjectProxies:
        if any(w in p.Desc.Name.lower() for w in ['voronoi','region intersection','boundary','map to surface','python','squish','surface morph']):
            report['proxies'].append({'name':p.Desc.Name,'guid':str(p.Guid),'type':str(p.Type)})
    import clr
    report['squisher_methods'] = [str(m) for m in clr.GetClrType(Rhino.Geometry.Squisher).GetMethods()]
except:
    report['error'] = traceback.format_exc()
with open('/Users/huiliu/UCB/26Fall/TDF/organic_ring_work/inspection.json','w') as f:
    json.dump(report,f,indent=2)
print('Organic ring inspection saved.')
