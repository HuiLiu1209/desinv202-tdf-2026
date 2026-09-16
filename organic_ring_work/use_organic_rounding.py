exec(compile(open('/Users/huiliu/UCB/26Fall/TDF/organic_ring_work/gh_helpers.py').read(),'gh_helpers.py','exec'))
def find(g):return doc.FindObject(System.Guid(g),False)
r={}
try:
    doc.Enabled=True
    rounder=find('9777a8d8-33dd-4968-8f5d-5365c5f7161d')
    p=rounder.Params.Input[1];p.Name=p.NickName='Smooth'
    p=rounder.CreateParameter(GH_ParameterSide.Input,2);p.Name=p.NickName='Diameter';p.Access=GH_ParamAccess.item;rounder.Params.RegisterInputParam(p)
    rounder.Params.OnParametersChanged()
    wire(find('287f171f-96cf-432d-8512-7d1bbf1a6c74'),rounder,2)
    rounder.Name=rounder.NickName='Organic Round + Size'
    rounder.Code=open(ROOT+'organic_round_mesh.py').read()
    rad=find('820e8340-138e-4851-8eee-703d16dccd91')
    rad.NickName='Roundness';rad.Slider.Type=GH_SliderAccuracy.Integer;rad.Slider.DecimalPlaces=0;rad.Slider.Minimum=System.Decimal(10);rad.Slider.Maximum=System.Decimal(100);rad.SetSliderValue(System.Decimal(80))
    old=find('dd433037-054a-41b4-a033-bed94328c616');old.RemoveAllSources();old.AddSource(find('91b36d8a-9eb2-417e-b5de-244238020968').Params.Output[2]);old.NickName='Offset Solid before rounding';old.Hidden=True
    mesh=find('5a268a6b-89e3-4801-84b8-bcf5f1b131ae');mesh.NickName='PRINT - Rounded Ring';mesh.Hidden=False;mesh.Attributes.Selected=True
    rounder.ExpireSolution(False);doc.NewSolution(False)
    r['counts']=[p.VolatileDataCount for p in rounder.Params.Output]
    r['errors']=list(rounder.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Error));r['warnings']=list(rounder.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Warning))
    for x in rounder.Params.Output[2].VolatileData.AllData(True):
        m=x.Value;r['mesh']={'valid':m.IsValid,'closed':m.IsClosed,'faces':m.Faces.Count,'vertices':m.Vertices.Count}
        for view in sc.doc.Views:
            if view.ActiveViewport.Name=='Perspective':
                box=m.GetBoundingBox(True);box.Inflate(3);view.ActiveViewport.ZoomBoundingBox(box)
    gh.Instances.ActiveCanvas.Refresh();sc.doc.Views.Redraw()
except:r['error']=traceback.format_exc()
with open(ROOT+'organic_round_result.json','w') as f:json.dump(r,f,indent=2)
