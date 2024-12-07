import pyautogui
import autoit
import os
import numpy as nm 
import pytesseract
import statistics
import math
import cv2 
import random
import time
import mouse
import numpy as np
from PIL import ImageGrab

# Bring WoW Client to the Foreground
autoit.win_activate("RuneLite")
autoit.win_move("RuneLite",856,0,1072,686)

# Change Directory to the Folder this script is in
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def smooth_move(x2, y2):
    # Width 1242
    # Height 686
    x1, y1 = mouse.get_position()
    if (abs(x2 - x1) > 750) or (abs(y2 - y1) > 750):
        amplitude = random.randint(75, 100)
        duration = random.uniform(1, 1.25)
    elif (abs(x2 - x1) > 350) or (abs(y2 - y1) > 500):
        amplitude = random.randint(50, 75)
        duration = random.uniform(0.75, 1)
    elif (abs(x2 - x1) > 50) or (abs(y2 - y1) > 50):
        amplitude = random.randint(25, 50)
        duration = random.uniform(0.5, .75)
    else:
        amplitude = random.randint(0, 25)
        duration = random.uniform(0.25, .5)

    points = []
    num_points = int(duration * 75)
    trig = random.randint(1, 4)

    for i in range(num_points + 1):
        # Linear interpolation between start and end positions
        ratio = i / num_points
        x = int(x1 + (x2 - x1) * ratio)

        # Use a sinusoidal function for y coordinates
        if trig == 1:  # Arc down (Sin + Sin Noise)
            y_variation = int(amplitude * math.sin(ratio * math.pi) + 0.2 * math.sin(30 * ratio))
        elif trig == 2:  # Arc down (Sin + Cos Noise)
            y_variation = int(amplitude * math.sin(ratio * math.pi) + .2 * math.cos(30 * ratio + (math.pi / 2)))
        elif trig == 3:  # Arc up (Cos + Sin Noise)
            y_variation = int(amplitude * math.sin(ratio * math.pi + math.pi) + .2 * math.sin(30 * ratio))
        elif trig == 4:  # Arc up (Cos + Cos Noise)
            y_variation = int(amplitude * math.sin(ratio * math.pi + math.pi) + .2 * math.cos(30 * ratio + (math.pi / 2)))

        y = int(y1 + (y2 - y1) * ratio + y_variation)
        points.append((x, y))

    for i, point in enumerate(points):
        x, y = point
        # Move the mouse to the calculated position
        mouse.move(x, y, absolute=True)

        # Calculate a sleep duration that increases in the middle of the path
        middle_ratio = abs(0.5 - (i / num_points))  # This will be 1 at the ends and 0 in the middle
        sleep_duration = duration * (0.5 + 0.5 * middle_ratio) / len(points)  # Customize the factors as needed
        time.sleep(sleep_duration)

    # Optional final pause
    time.sleep(random.uniform(.25, .5))

def ReadCompass():
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
        CompassAngle = CalculateAngle(((CompassWidth/2), (CompassHeight/2)), (x, y))
        return CompassX, CompassY, CompassWidth, CompassAngle

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

def randomXY(fileName):
    x, y, w, h = pyautogui.locateOnScreen(fileName, confidence=0.8)
    x, y, w, h = int(x), int(y), int(w), int(h)
    RandomX = random.randrange(x,x+w)
    RandomY = random.randrange(y,y+h)
    return RandomX, RandomY

def SetWorldMapPath(location):
    RandomX, RandomY = randomXY("Globe.png")
    smooth_move(RandomX ,RandomY)
    autoit.mouse_click("left")

    time.sleep(random.uniform(1,1.25))

    RandomX, RandomY = randomXY("WorldMap.png")
    smooth_move(RandomX ,RandomY)
    autoit.mouse_click("left")

    if location == "Lumbridge":
        smooth_move(1583 ,417) # Click on World Map
        autoit.mouse_click("left")
        time.sleep(random.uniform(.5,.75))

        x,y = randomXY("Lumbridge.png")
        smooth_move(x,y) # Click on the center of Lumbridge
        autoit.mouse_click("right")
        time.sleep(random.uniform(.5,.75))

        smooth_move(x + random.randint(-49,43),y + random.randint(35,48))
        autoit.mouse_click("left")
        time.sleep(random.uniform(.5,.75))

        smooth_move(1610 + random.randint(-9,9),53 + random.randint(-7,7)) # Click on World Map
        autoit.mouse_click("left")

def find_path(CompassX, CompassY, CompassWidth):
    MinimapX, MinimapY = int(CompassX + (CompassWidth/2) + 25), int(CompassY + 29)
    Minimap = pyautogui.screenshot(region=(MinimapX, MinimapY, 110, 110))
    Minimap.save("Minimap.png")

    # Get the width and height of the minimap
    width = Minimap.width
    height = Minimap.height
    
    # Convert the minimap to an array (if using PIL Image, you can convert to a NumPy array)
    compass_array = np.array(Minimap)

    # Define the target color
    target_color = (201, 132, 255)

    # Lists to store coordinates of the target color pixels
    XArray = []
    YArray = []

    # Iterate over each pixel in the minimap
    for x in range(width):
        for y in range(height):
            current_color = tuple(compass_array[y, x])  # Ensure the color is in tuple form
            if current_color == target_color:
                XArray.append(x)
                YArray.append(y)

    # Calculate distances from edges for all found pixels
    min_distance = 110
    closest_pixel = None

    for x, y in zip(XArray, YArray):
        # Calculate the distance to the nearest edge
        distance_to_edge = min(x, y, width - x - 1, height - y - 1)

        # Check if this pixel is the closest
        if distance_to_edge < min_distance:
            min_distance = distance_to_edge
            closest_pixel = (x + MinimapX, y + MinimapY)

    PathAngle = CalculateAngle((MinimapX+55,MinimapY + 55), closest_pixel)

    return closest_pixel, PathAngle

def rotateCamera(angle):
    x = random.randint(1278,1531)
    y = random.randint(300,400)
    if angle < 180 and angle > 45:
        dragDistance = 278 * (angle / 90)
        smooth_move(x,y)
        autoit.mouse_down("middle")
        smooth_move(x + dragDistance,y)
    elif angle > 180 and angle < 315: 
        dragDistance = 278 * ((360 - angle) / 90)
        smooth_move(x,y)
        autoit.mouse_down("middle")
        smooth_move(x - dragDistance,y)
    autoit.mouse_up("middle")

def followPath(PathPoint, PathAngle):
    print("Follow path")
    smooth_move(PathPoint)
    autoit.mouse_click()
    start = time.time()
    time.sleep(random.uniform(.5,.75))
    rotateCamera(PathAngle)
    if (autoit.pixel_get_color(1491,158) == 13543425):
        time.sleep(6 - time.time()-start)
    else:
        time.sleep(10 - time.time()-start)

while True:
    try:
        os.system('cls')
        CompassX, CompassY, CompassWidth, CompassAngle = ReadCompass()
        print("Angle of Map: " + str(round(CompassAngle,1)))

        PathPoint, PathAngle = find_path(CompassX, CompassY, CompassWidth)
        print("Angle of Path: " + str(round(PathAngle,1)))

        #SetWorldMapPath("Lumbridge")
        followPath()
        #rotateCamera(PathAngle)
        time.sleep(1)
                
    except Exception as e:
        print(e)