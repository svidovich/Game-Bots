import pyautogui
import autoit
import os
import math
import statistics
import cv2
import numpy as np
from PIL import Image 

# Bring WoW Client to the Foreground
# autoit.win_activate("RuneLite")

# Change Directory to the Folder this script is in
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def calculate_angle(center, point):
    # unpack the coordinates
    cx, cy = center  # center point
    px, py = point   # point on the circle

    # Calculate the difference in coordinates
    delta_x = px - cx
    delta_y = py - cy

    # Calculate angle in radians
    angle_radians = math.atan2(delta_y, delta_x)

    # Convert to degrees and adjust rotation
    angle_degrees = math.degrees(angle_radians)
    angle_degrees = (angle_degrees + 90) % 360

    return angle_degrees

WorldMap = cv2.imread("WorldMap.png")

while True:
    try:
        CompassX, CompassY, CompassWidth, CompassHeight = pyautogui.locateOnScreen("Compass.png", confidence=0.7)
        if CompassX:
            CompassX, CompassY, = int(CompassX), int(CompassY)
            CompassWidth, CompassHeight = int(CompassWidth), int(CompassHeight)
            Compass = pyautogui.screenshot(region=(CompassX, CompassY, CompassWidth, CompassHeight))
            Compass.save("CompassCurrent.png")
            XArray= []
            YArray=[]
            for x in range(CompassWidth):
                for y in range(CompassHeight):
                    current_color = Compass.getpixel((x, y))
                    if current_color == (49, 41, 29):
                        XArray.append(x)
                        YArray.append(y)

            if len(XArray) > 1:
                x = statistics.mean(XArray)
                y = statistics.mean(YArray)
            angle_degrees = calculate_angle(((CompassWidth/2), (CompassHeight/2)), (x, y))
            print("Angle of Map: " + str(round(angle_degrees,1)))

            Minimap = pyautogui.screenshot(region=(int(CompassX + (CompassWidth/2) + 25), CompassY + 29, 110, 110))
            Minimap.save("Minimap.png")

            Minimap = Image.open("Minimap.png").rotate(angle_degrees,3)
            Minimap.save("Minimap_Rotated.png")
            
            Minimap = cv2.imread("Minimap_Rotated.png")
            res = cv2.matchTemplate(WorldMap, Minimap, cv2.TM_CCOEFF_NORMED)
            loc = np.where(res >= .3)

            Length = 0
            for pt in zip(*loc[::-1]):
                if (Length == 0):
                    print(str(pt[0]) + ", " + str(pt[1]))
                    Length = 1
                
    except Exception as e:
        print(e)