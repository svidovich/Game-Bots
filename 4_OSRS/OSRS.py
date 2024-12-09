import pyautogui
import autoit
import os
import pytesseract
import statistics
import math
import random
import time
import mouse
import numpy as np
from PIL import Image, ImageGrab, ImageDraw

def smooth_move(x2, y2):
    x1, y1 = mouse.get_position()
    if (abs(x2 - x1) > 750) or (abs(y2 - y1) > 750):
        amplitude = random.randint(75, 100)
        duration = random.uniform(0.75, 1)
    elif (abs(x2 - x1) > 350) or (abs(y2 - y1) > 500):
        amplitude = random.randint(50, 75)
        duration = random.uniform(0.5, .75)
    elif (abs(x2 - x1) > 50) or (abs(y2 - y1) > 50):
        amplitude = random.randint(25, 50)
        duration = random.uniform(0.5, .75)
    else:
        amplitude = 0
        duration = random.uniform(0.25, .5)
    points = []
    num_points = int(duration * 75)
    trig = random.randint(1, 4)
    for i in range(num_points + 1):
        ratio = i / num_points
        x = int(x1 + (x2 - x1) * ratio)
        if trig == 1:
            y_variation = int(amplitude * math.sin(ratio * math.pi) + 0.2 * math.sin(30 * ratio))
        elif trig == 2:
            y_variation = int(amplitude * math.sin(ratio * math.pi) + .2 * math.cos(30 * ratio + (math.pi / 2)))
        elif trig == 3:
            y_variation = int(amplitude * math.sin(ratio * math.pi + math.pi) + .2 * math.sin(30 * ratio))
        elif trig == 4:
            y_variation = int(amplitude * math.sin(ratio * math.pi + math.pi) + .2 * math.cos(30 * ratio + (math.pi / 2)))
        y = int(y1 + (y2 - y1) * ratio + y_variation)
        points.append((x, y))
    for i, point in enumerate(points):
        x, y = point
        mouse.move(x, y, absolute=True)
        middle_ratio = abs(0.5 - (i / num_points))
        sleep_duration = duration * (0.5 + 0.5 * middle_ratio) / len(points)
        time.sleep(sleep_duration)
    time.sleep(random.uniform(.25, .5))

def findLocation():
    X1, Y1, X2, Y2 = autoit.win_get_pos("RuneLite")
    LocationText = pyautogui.screenshot(region=(X1 + 18, Y1 + 52, 126, 20))
    pytesseract.pytesseract.tesseract_cmd = r".\Tesseract-OCR\tesseract.exe"
    custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789,'
    string = pytesseract.image_to_string(LocationText, config=custom_config)
    X, Y, Height = string.split("\n")[0].split(",")
    X, Y, Height = int(X), int(Y), int(Height)
    return X, Y, Height

def readCompass():
    CompassX, CompassY, CompassWidth, CompassHeight = pyautogui.locateOnScreen("Compass.png", confidence=0.6)
    if CompassX:
        CompassX, CompassY = int(CompassX), int(CompassY)
        CompassWidth, CompassHeight = int(CompassWidth), int(CompassHeight)
        Compass = pyautogui.screenshot(region=(CompassX, CompassY, CompassWidth, CompassHeight))
        XArray, YArray = [], []
        for x in range(CompassWidth):
            for y in range(CompassHeight):
                current_color = Compass.getpixel((x, y))
                if current_color == (49, 41, 29):
                    XArray.append(x)
                    YArray.append(y)
        if len(XArray) > 1:
            x = statistics.mean(XArray)
            y = statistics.mean(YArray)
        CompassAngle = calculateAngle(((CompassWidth / 2), (CompassHeight / 2)), (x, y))
        return CompassX, CompassY, CompassWidth, CompassAngle

def calculateAngle(center, point):
    cx, cy = center
    px, py = point
    delta_x = px - cx
    delta_y = py - cy
    angle_radians = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle_radians)
    angle_degrees = (angle_degrees + 90) % 360
    return angle_degrees

def correctPath(CompassX, CompassY, CompassWidth, angleOfApproach):
    MinimapX, MinimapY = int(CompassX + (CompassWidth / 2) + 1), int(CompassY + 7)
    Minimap = pyautogui.screenshot(region=(MinimapX, MinimapY, 154, 154))
    Minimap.save("Minimap.png")
    CenterX, CenterY = MinimapX + 77, MinimapY + 77
    distance = random.randint(60, 70)
    dx = distance * math.cos(math.radians(angleOfApproach - 90))
    dy = distance * math.sin(math.radians(angleOfApproach - 90))
    smooth_move(CenterX + dx, CenterY + dy)
    autoit.mouse_click()
    if (autoit.pixel_get_color(1734, 157) == 12819969):
        time.sleep(3)
    else:
        time.sleep(7)

def setWorldMapPath(location):
    RandomX, RandomY = locateOnScreenRandom("Globe.png")
    smooth_move(RandomX, RandomY)
    autoit.mouse_click("left")
    time.sleep(random.uniform(1, 1.25))
    RandomX, RandomY = locateOnScreenRandom("WorldMap.png")
    smooth_move(RandomX, RandomY)
    autoit.mouse_click("left")
    if location == "Lumbridge":
        X1, Y1 = 1583, 417
    elif location == "WC_Regular":
        X1, Y1 = 1579, 400
    elif location == "GrandExchange":
        X1, Y1 = 1579, 400
    elif location == "SouthBank":
        X1, Y1 = 1578, 404

    smooth_move(X1, Y1)
    autoit.mouse_down("left")
    time.sleep(random.uniform(.2, .4))
    autoit.mouse_up("left")
    time.sleep(random.uniform(.5, .75))
    x, y = locateOnScreenRandom(location + ".png")
    smooth_move(x, y)
    autoit.mouse_click("right")
    time.sleep(random.uniform(.5, .75))
    smooth_move(x + random.randint(-49, 43), y + random.randint(35, 48))
    autoit.mouse_click("left")
    time.sleep(random.uniform(.5, .75))
    autoit.send("{Esc}", mode=0)

def locateOnScreenRandom(fileName, Region=None):
    if Region:
        x, y, w, h = pyautogui.locateOnScreen(fileName, confidence=0.35, region=Region)
    else:
        x, y, w, h = pyautogui.locateOnScreen(fileName, confidence=0.8)
    RandomX = random.randrange(x, x + w)
    RandomY = random.randrange(y, y + h)
    return RandomX, RandomY

def findPath(CompassX, CompassY, CompassWidth):
    MinimapX, MinimapY = int(CompassX + (CompassWidth / 2) + 1), int(CompassY + 7)
    Minimap = pyautogui.screenshot(region=(MinimapX, MinimapY, 154, 154))
    Minimap.save("Minimap.png")
    width = Minimap.width
    height = Minimap.height

    compass_array = np.array(Minimap)
    target_color = (201, 132, 255)
    XArray = []
    YArray = []
    for x in range(width):
        for y in range(height):
            current_color = tuple(compass_array[y, x])
            if current_color == target_color:
                XArray.append(x)
                YArray.append(y)
    max_distance = 200000
    min_distance = 10
    closest_pixel = None
    for x, y in zip(XArray, YArray):
        distance_to_edge = min(x, y, width - x - 1, height - y - 1)
        if distance_to_edge < max_distance and distance_to_edge > min_distance:
            max_distance = distance_to_edge
            PathPoint = (x + MinimapX, y + MinimapY)
    PathAngle = calculateAngle((MinimapX + 81, MinimapY + 81), PathPoint)
    return PathPoint, PathAngle

def rotateCamera(angle, limit=True):
    origX, origY = autoit.mouse_get_pos()
    x = random.randint(1278, 1531)
    y = random.randint(300, 400)
    if limit:
        top = 315
        bottom = 45
    else:
        top = 360
        bottom = 0
    if angle < 180 and angle > bottom:
        dragDistance = 278 * (angle / 90)
        smooth_move(x, y)
        autoit.mouse_down("middle")
        smooth_move(x + dragDistance, y)
    elif angle > 180 and angle < top:
        dragDistance = 278 * ((360 - angle) / 90)
        smooth_move(x, y)
        autoit.mouse_down("middle")
        smooth_move(x - dragDistance, y)
    autoit.mouse_up("middle")

def followPath(PathPoint, PathAngle):
    print("Follow path")
    smooth_move(PathPoint[0], PathPoint[1])
    autoit.mouse_click()
    startTime = time.time()
    time.sleep(random.uniform(.4, .6))
    rotateCamera(PathAngle)
    if (autoit.pixel_get_color(1734, 157) == 12819969):
        time.sleep(3 - (time.time() - startTime))
    else:
        time.sleep(7 - (time.time() - startTime))

def pathLoop():
    while True:
        CompassX, CompassY, CompassWidth, CompassAngle = readCompass()
        print("Angle of Player: " + str(round(CompassAngle, 1)))
        try:
            PathPoint, PathAngle = findPath(CompassX, CompassY, CompassWidth)
            print("Angle of Path: " + str(round(PathAngle, 1)))
            followPath(PathPoint, PathAngle)
        except:
            print("Path Complete")
            break

def highlight_color_on_screen(color, tolerance, region, drawLoc=False):
    screenshot = pyautogui.screenshot().convert("RGB")
    screenshot_np = np.array(screenshot)
    x1, y1, x2, y2 = region
    points = []
    for x in range(x1, x2):
        for y in range(y1, y2):
            current_color = screenshot_np[y, x]
            if np.all(np.abs(np.array(current_color) - np.array(color)) <= tolerance):
                if drawLoc:
                    draw = ImageDraw.Draw(screenshot)
                    draw.rectangle([x, y, x + 1, y + 1], outline="red", width=1)
                else:
                    points.append((x, y))
    if drawLoc:
        draw.rectangle((x1, y1, x2, y2), outline="blue", width=1)
        screenshot.show()
    else:
        return points

def allInfo(X2, Y2):
    os.system('cls')
    X, Y, Height = findLocation()
    print("Location: " + str(X) + ", " + str(Y))

    Distance = math.sqrt((X2 - X) ** 2 + (Y2 - Y) ** 2)
    print("Distance: " + str(Distance))

    CompassX, CompassY, CompassWidth, CompassAngle = readCompass()
    print("Angle of Player: " + str(round(CompassAngle, 1)))

    DirectionAngle = calculateAngle((0, 0), (X2 - X, Y - Y2))
    print("Angle of Destination: " + str(round(DirectionAngle, 1)))

    angleOfApproach = (DirectionAngle - 360) + CompassAngle
    print("Angle of Approach: " + str(round(angleOfApproach, 1)))

    return Distance, CompassX, CompassY, CompassWidth, angleOfApproach

def CutWood(X2, Y2):
    X2 = location[0]
    Y2 = location[1]
    while True:
        _, _, _, _, angleOfApproach = allInfo(X2, Y2)
        try:
            treeLocs = highlight_color_on_screen((38, 44, 11), 1, region=(957, 110, 1834, 635), drawLoc=False)
            middleTree = min(treeLocs, key=lambda loc: abs(loc[0] - sum([loc[0] for loc in treeLocs]) / len([loc[0] for loc in treeLocs])))
            smooth_move(middleTree[0], middleTree[1])
            if (pyautogui.locateOnScreen("TealIndicator.png", confidence=0.8)):
                autoit.mouse_click()
                while pyautogui.locateOnScreen("WoodcuttingBoolean.png", confidence=0.8):
                    time.sleep(.01)
            else:
                continue
        except Exception as e:
            print(e)
        rotateCamera(angleOfApproach, limit=False)

def BankWood(X2, Y2):
    while True:
        try:
            Distance, _, _, _, angleOfApproach = allInfo(X2, Y2)
            if Distance < 10:
                print("Find Teller")
                tellerLocs = highlight_color_on_screen((39, 32, 52), 1, region=(957, 110, 1834, 635), drawLoc=False)
                middleTeller = min(tellerLocs, key=lambda loc: abs(loc[0] - sum([loc[0] for loc in tellerLocs]) / len([loc[0] for loc in tellerLocs])))
                smooth_move(middleTeller[0], middleTeller[1])
                
                try:
                    A, A2 = locateOnScreenRandom("TalkToBanker.png")
                except:
                    A, A2 = False, False

                try:
                    B, B2 = locateOnScreenRandom("BankBooth.png")
                except:
                    B, B2 = False, False

                if A or B:
                    autoit.mouse_click("right")
                    time.sleep(random.uniform(.4, .6))
                    RandomX, RandomY = locateOnScreenRandom("BankBanker.png")
                    smooth_move(RandomX, RandomY)
                    autoit.mouse_click("left")

                    time.sleep(random.uniform(5,6))
                    smooth_move(1826, 612)
                    autoit.mouse_click("left")
                    time.sleep(random.uniform(.4, .6))
                    autoit.send("{Esc}", mode=0)
                    break
            else:
                setWorldMapPath("SouthBank")
                pathLoop()
        except Exception as e:
            print(e)
            rotateCamera(angleOfApproach, limit=False)

def WoodCutter(type, X2, Y2):
    while True:
        try:
            Distance, CompassX, CompassY, CompassWidth, angleOfApproach = allInfo(X2, Y2)

            if (autoit.pixel_get_color(1826, 612) == 7229226):
                print("Inventory is full")
                BankWood(3183, 3438)
            else:
                if (Distance < 50) and (Distance > 10):
                    print("Short Run")
                    correctPath(CompassX, CompassY, CompassWidth, angleOfApproach)
                elif (Distance < 3000) and (Distance > 50):
                    print("Long Run")
                    setWorldMapPath("WC_" + str(type) + "2")
                    pathLoop()
                else:
                    print("Cut Wood")
                    CutWood(X2, Y2)
            time.sleep(1)
        except Exception as e:
            print(e)

# Bring Runescape Client to the Foreground
autoit.win_activate("RuneLite")
autoit.win_move("RuneLite", 856, 0, 1072, 686)  # Resize
# Change Directory to the Folder this script is in
os.chdir(os.path.dirname(os.path.abspath(__file__)))

WoodCutter("Regular", 3164, 3398)