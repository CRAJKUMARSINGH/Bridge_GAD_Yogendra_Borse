# Import the modules required 
import ezdxf
import os
import pyautogui 
import time
# Create a DXF R2010 document and use default setup 
doc = ezdxf.new("R2010", setup = True)

# Spiral square Autocad drawing using pyautogui # it starts at 300 units then reduce by 20 unit time.sleep(3)
distance = 300
pyautogui.typewrite("pline")
pyautogui.press('enter')
while distance > 0:
    pyautogui.leftClick() 
    pyautogui.dragRel (distance, 0) 
    pyautogui.leftClick()
distance = distance - 20
pyautogui.dragRel(0, distance)
pyautogui.leftClick()
pyautogui.dragRel(-distance, 0 ) 
pyautogui.leftClick()
distance = disTANCE -20 
time.sleep(3)
pyautogui.dragRel(0 , -distance) 

# Save the drawing as spiral.dxf
doc.saveas(r"C:\Users\Rajkumar Singh\Downloads\P1\spiral.dxf")

# Save the drawing as dim.dxf in specified directory
doc.saveas(os.path.join(directory, filename))


