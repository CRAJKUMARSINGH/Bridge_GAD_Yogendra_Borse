from pyautocad import Autocad, APoint
# Create Autocad instance
acad= Autocad (create_if_not_exists=True) 
acad.prompt("Hello, Autocad from Python\n") 
print(acad.doc.Name)

acad.model

# Draw by adding text, line and circle

p1 = APoint(0, 0)
p2 = APoint (50, 25)
for i in range(5):
    text = acad.model.AddText(u'Circle %s' % i, p1, 2.5)
    acad.model.AddLine(p1, p2)
    acad.model.AddCircle(p1, 10)
    p1.y += 30
    ##for obj in acad.iter_objects():
    #print(obj.ObjectId)
    ####saved in x.dwg


