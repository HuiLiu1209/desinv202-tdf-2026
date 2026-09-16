import Rhino
import Grasshopper as gh
import System
import System.Drawing as drawing
import scriptcontext as sc
import json,traceback
from Grasshopper.Kernel import GH_ParamAccess, GH_DataMapping, GH_ParameterSide
from Grasshopper.Kernel.Types import GH_Integer
from Grasshopper.Kernel.Special import GH_NumberSlider, GH_Group, GH_Panel
from Grasshopper.GUI.Base import GH_SliderAccuracy

ROOT='/Users/huiliu/UCB/26Fall/TDF/organic_ring_work/'
r={}
created=[]
doc=gh.Instances.ActiveCanvas.Document

def add(obj,x,y):
    obj.CreateAttributes()
    obj.Attributes.Pivot=drawing.PointF(x,y)
    doc.AddObject(obj,False)
    created.append(obj)
    return obj

def component(name,x,y):
    proxies=[p for p in gh.Instances.ComponentServer.ObjectProxies if p.Desc.Name==name and not p.Obsolete]
    obj=proxies[0].CreateInstance()
    return add(obj,x,y)

def slider(name,value,lo,hi,x,y,integer=False):
    obj=GH_NumberSlider()
    obj.NickName=name
    obj.Slider.Type=GH_SliderAccuracy.Integer if integer else GH_SliderAccuracy.Float
    obj.Slider.DecimalPlaces=0 if integer else 2
    obj.Slider.Minimum=System.Decimal(lo)
    obj.Slider.Maximum=System.Decimal(hi)
    obj.SetSliderValue(System.Decimal(value))
    return add(obj,x,y)

def script(name,filename,inputs,outputs,x,y):
    obj=gh.Instances.ComponentServer.EmitObjectProxy(System.Guid('410755b1-224a-4c1e-a407-bf32fb45ea7e')).CreateInstance()
    while obj.Params.Input.Count>len(inputs):obj.Params.UnregisterInputParameter(obj.Params.Input[obj.Params.Input.Count-1],True)
    while obj.Params.Input.Count<len(inputs):
        obj.Params.RegisterInputParam(obj.CreateParameter(GH_ParameterSide.Input,obj.Params.Input.Count))
    for p,spec in zip(obj.Params.Input,inputs):
        p.Name=p.NickName=spec[0]
        p.Access=spec[1]
        p.Optional=False
        if p.Access==GH_ParamAccess.list:p.DataMapping=GH_DataMapping.Flatten
    while obj.Params.Output.Count<len(outputs)+1:
        obj.Params.RegisterOutputParam(obj.CreateParameter(GH_ParameterSide.Output,obj.Params.Output.Count))
    for p,name_out in zip(list(obj.Params.Output)[1:],outputs):
        p.Name=p.NickName=name_out
    obj.Params.OnParametersChanged()
    obj.Name=obj.NickName=name
    obj.Description=name+' - self-contained RhinoCommon script; double-click to inspect.'
    obj.Code=open(ROOT+filename).read()
    return add(obj,x,y)

def wire(source,target,index,output=0):
    target.Params.Input[index].AddSource(source.Params.Output[output] if hasattr(source,'Params') else source)

try:
    uv=doc.FindObject(System.Guid('9f9fbb64-896a-4293-8be2-cfa9a4b38141'),False)
    pop=doc.FindObject(System.Guid('3480a039-c04d-4edd-939a-e39d04d9d65a'),False)
    if not uv or not pop:raise ValueError('Existing UVSurface/Populate nodes not found.')
    count=slider('Cell count',40,8,150,750,1220,True)
    seed=slider('Pattern seed',6,0,100,750,1270,True)
    wire(count,pop,1);wire(seed,pop,2)
    outline=script('UV Boundary','uv_boundary.py',[('U',GH_ParamAccess.item)],['Boundary','Bounds'],1050,1430)
    wire(uv,outline,0)
    vor=component('Voronoi',1280,1090)
    wire(pop,vor,0);wire(outline,vor,2,2)
    clip=component('Region Intersection',1510,1090)
    clip.NickName='Clip to UV'
    wire(vor,clip,0);wire(outline,clip,1,1)
    clip.Params.Input[0].DataMapping=GH_DataMapping.Graft
    clip.Params.Input[1].DataMapping=GH_DataMapping.Flatten
    area=component('Area',1700,1240)
    wire(clip,area,0)
    scale=component('Scale',1910,1110)
    wire(clip,scale,0);wire(area,scale,1,1)
    factor=slider('Hole scale',0.76,0.3,0.95,1620,1370)
    wire(factor,scale,2)
    fillet=component('Fillet',2140,1100)
    wire(scale,fillet,0)
    rounding=slider('Corner radius mm',1.0,0.0,4.0,1820,1430)
    wire(rounding,fillet,1)
    mapper=script('Squish Back to Ring','squish_back.py',[('U',GH_ParamAccess.item),('Cells',GH_ParamAccess.list),('Holes',GH_ParamAccess.list)],['Cells3D','Holes3D','Report'],2390,1120)
    wire(uv,mapper,0);wire(clip,mapper,1);wire(fillet,mapper,2)
    outcells=gh.Kernel.Parameters.Param_Curve();outcells.NickName='Voronoi on Ring';add(outcells,2690,1040);outcells.AddSource(mapper.Params.Output[1])
    outholes=gh.Kernel.Parameters.Param_Curve();outholes.NickName='Rounded Holes on Ring';add(outholes,2690,1140);outholes.AddSource(mapper.Params.Output[2])
    report=GH_Panel();add(report,2650,1290);report.AddSource(mapper.Params.Output[3]);report.Attributes.Bounds=drawing.RectangleF(2650,1290,330,100)
    note=GH_Panel();note.UserText='NON-RECTANGULAR UV / SQUISH WORKFLOW\nPopulate -> Voronoi -> clip to real UV boundary -> Scale + Fillet -> SquishBack.\nCell count / Pattern seed / Hole scale / Corner radius control the pattern.\nSquish data is required. These outputs are curves, ready for surface cutting.\nCurrent dimensions are preserved.';add(note,690,1500);note.Attributes.Bounds=drawing.RectangleF(690,1500,550,150)
    for obj in created:
        if hasattr(obj,'Hidden'):obj.Hidden=True
    uv.Hidden=True;pop.Hidden=True
    fillet.Hidden=False
    outcells.Hidden=False
    outholes.Hidden=True
    group=GH_Group();group.NickName='ORGANIC RING | NON-RECTANGULAR UV -> VORONOI -> SQUISHBACK';group.Colour=drawing.Color.FromArgb(45,120,180)
    for obj in created:group.AddObject(obj.InstanceGuid)
    group.AddObject(uv.InstanceGuid);group.AddObject(pop.InstanceGuid)
    doc.AddObject(group,False)
    doc.NewSolution(False)
    r['nodes']=[]
    for obj in created:
        row={'id':str(obj.InstanceGuid),'name':obj.NickName,'type':str(obj.GetType())}
        if hasattr(obj,'RuntimeMessages'):
            row['errors']=list(obj.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Error))
            row['warnings']=list(obj.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Warning))
        if hasattr(obj,'Params'):row['output_counts']=[p.VolatileDataCount for p in obj.Params.Output]
        r['nodes'].append(row)
    gh.Instances.ActiveCanvas.Refresh()
except:
    r['error']=traceback.format_exc()
with open(ROOT+'build_result.json','w') as f:json.dump(r,f,indent=2)
print('Voronoi workflow built; see build_result.json for validation.')
