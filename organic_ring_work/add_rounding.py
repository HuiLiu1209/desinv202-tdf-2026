exec(compile(open('/Users/huiliu/UCB/26Fall/TDF/organic_ring_work/gh_helpers.py').read(),'gh_helpers.py','exec'))
from Grasshopper.Kernel.Types import GH_Number
def find(g):return doc.FindObject(System.Guid(g),False)
r={}
try:
    doc.Enabled=True
    diameter=find('287f171f-96cf-432d-8512-7d1bbf1a6c74')
    diameter.NickName='INNER DIAMETER mm'
    diameter.Slider.Type=GH_SliderAccuracy.Float;diameter.Slider.DecimalPlaces=2;diameter.Slider.Minimum=System.Decimal(14);diameter.Slider.Maximum=System.Decimal(30);diameter.SetSliderValue(System.Decimal(22))
    half=component('Division',350,185);half.NickName='Diameter / 2'
    wire(diameter,half,0);half.Params.Input[1].PersistentData.Append(GH_Number(2.0))
    circle=find('99532d9c-df9f-418b-bcc2-756edcd0f18a');circle.Params.Input[1].RemoveAllSources();wire(half,circle,1)
    rounder=script('Round ALL Edges','round_edges.py',[('Brep',GH_ParamAccess.item),('Radius',GH_ParamAccess.item)],['Rounded','PrintMesh','Report'],3380,1070)
    wire(find('91b36d8a-9eb2-417e-b5de-244238020968'),rounder,0,2)
    rad=slider('ALL edge round mm',0.5,0.15,0.7,3030,1550);wire(rad,rounder,1)
    output=find('dd433037-054a-41b4-a033-bed94328c616');output.RemoveAllSources();output.AddSource(rounder.Params.Output[1]);output.Attributes.Pivot=drawing.PointF(3690,1050)
    mesh=find('5a268a6b-89e3-4801-84b8-bcf5f1b131ae');mesh.RemoveAllSources();mesh.AddSource(rounder.Params.Output[2]);mesh.Attributes.Pivot=drawing.PointF(3690,1150)
    panel=find('68ecb628-1b59-481f-8cfa-bc32b9e7ac79');panel.RemoveAllSources();panel.AddSource(rounder.Params.Output[3])
    for o in created:
        if hasattr(o,'Hidden'):o.Hidden=True
    doc.NewSolution(True)
    r['created']=[{'id':str(o.InstanceGuid),'name':o.NickName} for o in created]
    for obj in [find('91b36d8a-9eb2-417e-b5de-244238020968'),rounder]:
        r[obj.NickName]={'counts':[p.VolatileDataCount for p in obj.Params.Output],'errors':list(obj.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Error)),'warnings':list(obj.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Warning))}
    gh.Instances.ActiveCanvas.Refresh();sc.doc.Views.Redraw()
except:r['error']=traceback.format_exc()
with open(ROOT+'rounding_result.json','w') as f:json.dump(r,f,indent=2)
print('Diameter and edge rounding updated.')
