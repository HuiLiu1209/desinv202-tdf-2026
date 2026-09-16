exec(compile(open('/Users/huiliu/UCB/26Fall/TDF/organic_ring_work/gh_helpers.py').read(),'gh_helpers.py','exec'))
import clr
clr.AddReference('GH_IO')
import GH_IO
r={}
def find(g):return doc.FindObject(System.Guid(g),False)
try:
    archive=GH_IO.Serialization.GH_Archive();archive.AppendObject(doc,'Definition')
    archive.WriteToFile(ROOT+'Before_Live_Solid.gh',True,False)
    loft=find('49e8e1f5-36f7-465f-9d52-6c9bafccdce7')
    uv=find('9f9fbb64-896a-4293-8be2-cfa9a4b38141')
    live=script('Live Loft Unwrap','live_unwrap.py',[('Loft',GH_ParamAccess.item)],['UV'],640,1080)
    wire(loft,live,0)
    uv.RemoveAllSources();uv.AddSource(live.Params.Output[1]);uv.NickName='UV from Loft'
    uv.Attributes.Pivot=drawing.PointF(880,1080)
    clip=find('034aada3-b665-419b-a4a8-348e8499b68e')
    inset=script('Print Spacing','inset_for_print.py',[('Cells',GH_ParamAccess.list),('U',GH_ParamAccess.item),('Web',GH_ParamAccess.item),('Rim',GH_ParamAccess.item)],['SafeCells'],1610,1080)
    wire(clip,inset,0);wire(uv,inset,1)
    web=slider('Min bridge mm',1.4,0.7,3.0,1220,1540)
    rim=slider('Edge rim mm',1.2,0.6,3.0,1220,1590)
    wire(web,inset,2);wire(rim,inset,3)
    area=find('4f261cbb-ad6b-48e8-ad73-652030780587')
    scale=find('22226ffa-9a6a-41b9-9437-9697619a8a73')
    for obj in (area,scale):obj.Params.Input[0].RemoveAllSources();wire(inset,obj,0,1)
    factor=find('253a165d-0fca-43f4-8583-0c036a0514bb');factor.SetSliderValue(System.Decimal(0.9))
    mapper=find('ad095307-9c63-4711-a6e7-206f2a684495')
    solid=script('Cut Loft + Solid Offset','solid_from_loft.py',[('Loft',GH_ParamAccess.item),('Holes',GH_ParamAccess.list),('Thickness',GH_ParamAccess.item)],['Perforated','Solid','PrintMesh','Report'],3000,1110)
    wire(loft,solid,0);wire(mapper,solid,1,2)
    thick=slider('Wall thickness mm',1.6,0.8,3.0,2600,1450)
    wire(thick,solid,2)
    result=gh.Kernel.Parameters.Param_Brep();result.NickName='PRINTABLE RING';add(result,3320,1080);result.AddSource(solid.Params.Output[2])
    mesh=gh.Kernel.Parameters.Param_Mesh();mesh.NickName='STL Mesh';add(mesh,3320,1170);mesh.AddSource(solid.Params.Output[3])
    panel=GH_Panel();add(panel,3230,1320);panel.AddSource(solid.Params.Output[4]);panel.Attributes.Bounds=drawing.RectangleF(3230,1320,420,160)
    # Only preview the finished ring. The upstream Loft remains fully connected.
    for obj in doc.Objects:
        if hasattr(obj,'Hidden'):obj.Hidden=True
        obj.Attributes.Selected=False
    result.Hidden=False
    result.Attributes.Selected=True
    doc.NewSolution(False)
    r['created']=[{'id':str(o.InstanceGuid),'name':o.NickName} for o in created]
    r['nodes']=[]
    for o in doc.Objects:
        if o in created or o in (uv,area,scale,mapper):
            row={'id':str(o.InstanceGuid),'name':o.NickName}
            if hasattr(o,'Params'):row['counts']=[p.VolatileDataCount for p in o.Params.Output]
            if hasattr(o,'RuntimeMessages'):row['errors']=list(o.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Error));row['warnings']=list(o.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Warning))
            r['nodes'].append(row)
    gh.Instances.ActiveCanvas.Refresh();sc.doc.Views.Redraw()
except:r['error']=traceback.format_exc()
with open(ROOT+'upgrade_result.json','w') as f:json.dump(r,f,indent=2)
print('Live solid workflow updated.')
