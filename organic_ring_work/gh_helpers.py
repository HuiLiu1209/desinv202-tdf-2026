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
