import Rhino as R
import Grasshopper as G
import System
import scriptcontext as sc
import clr,json,traceback
from System.Collections.Generic import List
r={}
try:
    U=sc.doc.Objects.FindId(System.Guid('a5f31448-51ea-43f6-8400-f3a7a429b2b2')).Geometry
    T=sc.doc.Objects.FindId(System.Guid('9f4b7a84-0df9-431b-9b62-1de7d7929990')).Geometry
    r['squished']=R.Geometry.Squisher.Is2dPatternSquished(U)
    edges=R.Geometry.Curve.JoinCurves(U.DuplicateNakedEdgeCurves(True,False),0.01)
    marks=List[R.Geometry.GeometryBase](edges)
    mapped=R.Geometry.Squisher.SquishBack2dMarks(U,marks)
    r['mapped']=[]
    if mapped:
        for c in mapped:
            r['mapped'].append({'type':str(c.GetType()) if c else None,'bbox':str(c.GetBoundingBox(True)) if c else None})
    py=G.Instances.ComponentServer.EmitObjectProxy(System.Guid('410755b1-224a-4c1e-a407-bf32fb45ea7e')).CreateInstance()
    r['pyproperties']=[str(p) for p in py.GetType().GetProperties()]
    r['pyinputtypes']=[str(p.GetType()) for p in py.Params.Input]
    r['pymethods']=[str(m) for m in py.GetType().GetMethods() if any(n in m.Name for n in ['Parameter','Code','Variable'])]
except:
    r['error']=traceback.format_exc()
with open('/Users/huiliu/UCB/26Fall/TDF/organic_ring_work/probe.json','w') as f:json.dump(r,f,indent=2)
print('Mapping probe saved.')
