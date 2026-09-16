import Rhino.Geometry as rg
import System
import rhinoscriptsyntax as rs
tol=0.001
def geom(x):
    if hasattr(x,'Value'):x=x.Value
    if isinstance(x,System.Guid):x=rs.coercegeometry(x)
    return x
def inward(c,d):
    original=rg.AreaMassProperties.Compute(c).Area
    candidates=[]
    for sign in (-1,1):
        result=c.Offset(rg.Plane.WorldXY,sign*d,tol,rg.CurveOffsetCornerStyle.Sharp)
        if result:
            for q in result:
                if q.IsClosed and rg.AreaMassProperties.Compute(q).Area<original-tol:
                    candidates.append(q)
    return candidates
b=geom(U)
if isinstance(b,rg.Surface):b=b.ToBrep()
boundaries=rg.Curve.JoinCurves(b.DuplicateNakedEdgeCurves(True,False),tol)
limits=[]
for boundary in boundaries:limits.extend(inward(boundary,max(float(Rim),0.3)))
if not limits:raise ValueError('Rim width is too large for this ring.')
SafeCells=[]
for cell in Cells:
    for q in inward(geom(cell),max(float(Web),0.5)*0.5):
        for boundary in limits:
            cuts=rg.Curve.CreateBooleanIntersection(q,boundary,tol)
            if cuts:
                for c in cuts:
                    if c.IsClosed and rg.AreaMassProperties.Compute(c).Area>0.08:SafeCells.append(c)
if not SafeCells:raise ValueError('No holes remain. Reduce cell count or connection width.')
ghenv.Component.Message='Web >= {:.2f} mm (flat)'.format(float(Web))
