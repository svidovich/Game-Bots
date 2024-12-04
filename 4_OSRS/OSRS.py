import pyautogui
import autoit
import os
import math
import statistics

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

    # Convert to degrees if needed
    angle_degrees = math.degrees(angle_radians)
    angle_degrees = (angle_degrees + 90) % 360

    return angle_radians, angle_degrees

while True:
    try:
        CompassX, CompassY, CompassWidth, CompassHeight = pyautogui.locateOnScreen("Compass.png", confidence=0.75)
        if CompassX:
            CompassX, CompassY, CompassWidth, CompassHeight = int(CompassX), int(CompassY), int(CompassWidth), int(CompassHeight)
            #print(str(CompassX) + ", " + str(CompassY) + ", " + str(CompassWidth) + ", " + str(CompassHeight))

            image = pyautogui.screenshot(region=(CompassX, CompassY, CompassWidth, CompassHeight))
            image.save("CompassCurrent.png")
            XArray= []
            YArray=[]
            for x in range(CompassWidth):
                for y in range(CompassHeight):
                    current_color = image.getpixel((x, y))
                    if current_color == (49, 41, 29):
                        XArray.append(x)
                        YArray.append(y)
                        break

            x = statistics.mean(XArray)
            y = statistics.mean(YArray)
            angle_radians, angle_degrees = calculate_angle(((CompassWidth/2), (CompassHeight/2)), (x, y))
            #print("Found Color at: " + str(x - CenterX) + ", " + str(CompassY - y))
            print("Angle of Map: " + str(round(angle_degrees,1)))
    except Exception as e:
        print("No Compass")