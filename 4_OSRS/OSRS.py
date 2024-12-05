import pyautogui
import autoit
import os
import numpy as nm 
import pytesseract
import statistics
import math
import cv2 
from PIL import ImageGrab 

# Bring WoW Client to the Foreground
# autoit.win_activate("RuneLite")

# Change Directory to the Folder this script is in
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def FindLocationFromPlugin():
    X1, Y1, X2, Y2 = autoit.win_get_pos("RuneLite")
    LocationText = pyautogui.screenshot(region=(X1+18, Y1+52, 126, 20))
    pytesseract.pytesseract.tesseract_cmd = r".\Tesseract-OCR\tesseract.exe"

    # Only Find Numbers
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789,'

    # Pull Location Text
    string = pytesseract.image_to_string(LocationText,config=custom_config)

    # Split by line, then split by commas
    X, Y, Height = string.split("\n")[0].split(",")

    return X, Y, Height

def CalculateAngle(center, point):
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

while True:
    try:
        CompassX, CompassY, CompassWidth, CompassHeight = pyautogui.locateOnScreen("Compass.png", confidence=0.7)
        if CompassX:
            CompassX, CompassY, = int(CompassX), int(CompassY)
            CompassWidth, CompassHeight = int(CompassWidth), int(CompassHeight)
            Compass = pyautogui.screenshot(region=(CompassX, CompassY, CompassWidth, CompassHeight))
            XArray, YArray= [], []
            for x in range(CompassWidth):
                for y in range(CompassHeight):
                    current_color = Compass.getpixel((x, y))
                    if current_color == (49, 41, 29):
                        XArray.append(x)
                        YArray.append(y)

            if len(XArray) > 1:
                x = statistics.mean(XArray)
                y = statistics.mean(YArray)
            
            angle_degrees = CalculateAngle(((CompassWidth/2), (CompassHeight/2)), (x, y))
            print("Angle of Map: " + str(round(angle_degrees,1)))
            
            # Find Location on the World Map
            X, Y, Height = FindLocationFromPlugin()
            print(X + ", " + Y + ", " + Height)
                
    except Exception as e:
        print(e)