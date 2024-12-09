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

# Human Movement of Mouse
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

# X, Y, Height of Player
def findLocation(drawLoc = False):
    X1, Y1, X2, Y2 = autoit.win_get_pos("RuneLite")
    LocationText = pyautogui.screenshot(region=(X1 + 53, Y1 + 52, 91, 20))
    if drawLoc == True:
        LocationText.show()
    pytesseract.pytesseract.tesseract_cmd = r".\Tesseract-OCR\tesseract.exe"
    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789,'
    string = pytesseract.image_to_string(LocationText, config=custom_config)
    X, Y, Height = string.split("\n")[0].split(",")
    X, Y, Height = int(X), int(Y), int(Height)
    return X, Y, Height

#  Compass Info
#  CompassX, CompassY, CompassWidth, CompassAngle
def readCompass():
    CompassX, CompassY, CompassWidth, CompassHeight = pyautogui.locateOnScreen("Compass.png", confidence=0.65)
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

# Angle between Center and Point
def calculateAngle(center, point):
    cx, cy = center
    px, py = point
    delta_x = px - cx
    delta_y = py - cy
    angle_radians = math.atan2(delta_y, delta_x)
    angle_degrees = math.degrees(angle_radians)
    angle_degrees = (angle_degrees + 90) % 360
    return angle_degrees

# Set WorldMap Path
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
    elif location == "Regular":
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

# Locate Image on Screen
# Randomize X, Y
def locateOnScreenRandom(fileName, confidence=0.8, Region=None):
    if Region:
        x, y, w, h = pyautogui.locateOnScreen(fileName, confidence=0.35, region=Region)
    else:
        x, y, w, h = pyautogui.locateOnScreen(fileName, confidence=confidence)
    RandomX = random.randrange(x, x + w)
    RandomY = random.randrange(y, y + h)
    return RandomX, RandomY

# Rotate Camera by Angle
# Don't rotate near 0 deg if limit is set
def rotateCamera(angle, limit=True):
    origX, origY = autoit.mouse_get_pos()
    x = random.randint(1278, 1531)
    y = random.randint(300, 400)
    if angle < 0:
        angle = angle + 360

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

# Short Runs w/ Minimap
# Click towards Target
def correctPath(CompassX, CompassY, CompassWidth, angleOfApproach, Distance):
    MinimapX, MinimapY = int(CompassX + (CompassWidth / 2) + 1), int(CompassY + 7)
    Minimap = pyautogui.screenshot(region=(MinimapX, MinimapY, 154, 154))
    Minimap.save("Minimap.png")
    CenterX, CenterY = MinimapX + 77, MinimapY + 77
    if Distance > 20:
        mapDistance = random.randint(60, 70)
    elif Distance > 10:
        mapDistance = random.randint(30, 35)
    elif Distance > 0:
        mapDistance = random.randint(15, 18)
    dx = mapDistance * math.cos(math.radians(angleOfApproach - 90))
    dy = mapDistance * math.sin(math.radians(angleOfApproach - 90))
    smooth_move(CenterX + dx, CenterY + dy)
    autoit.mouse_click()
    startTime = time.time()
    rotateCamera(angleOfApproach)
    if (autoit.pixel_get_color(1734, 157) == 12819969):
        time.sleep(2.5 - (time.time() - startTime))
    else:
        time.sleep(6.5 - (time.time() - startTime))

# Long Runs w/ the path set by setWorldMapPath()
# Find Pink Path
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

# Long Runs w/ the path set by setWorldMapPath()
# Click Pink Path found via findPath()
def pathLoop():
    while True:
        CompassX, CompassY, CompassWidth, CompassAngle = readCompass()
        print("Angle of Player: " + str(round(CompassAngle, 1)))
        try:
            PathPoint, PathAngle = findPath(CompassX, CompassY, CompassWidth)
            print("Angle of Path: " + str(round(PathAngle, 1)))
            smooth_move(PathPoint[0], PathPoint[1])
            autoit.mouse_click()
            startTime = time.time()
            time.sleep(random.uniform(.4, .6))
            rotateCamera(PathAngle)
            if (autoit.pixel_get_color(1734, 157) == 12819969):
                time.sleep(2.5 - (time.time() - startTime))
            else:
                time.sleep(6.5 - (time.time() - startTime))
        except:
            print("Path Complete")
            break

# Find Color On Screen (Such as Tree Color)
def highlight_color_on_screen(color, tolerance, region, sections = 30, drawLoc=False):
    if drawLoc:
        startTime = time.time()
    x1, y1, x2, y2 = region
    results = []

    Regions = sections

    width = x2 - x1
    height = y2 - y1
    sub_width = width // Regions  # Divide into columns
    sub_height = height // Regions  # Divide into rows

    # Loop through each sub-region
    for i in range(Regions):
        for j in range(Regions):
            sub_x1 = x1 + (j * sub_width)
            sub_y1 = y1 + (i * sub_height)
            sub_x2 = sub_x1 + sub_width
            sub_y2 = sub_y1 + sub_height

            try:
                result = autoit.pixel_search(sub_x1, sub_y1, sub_x2, sub_y2, color, tolerance)
                results.append(result)  # Append found point to results
            except:
                result = None

    if drawLoc:
        # Get the screenshot and draw rectangles for each found point
        screenshot = pyautogui.screenshot().convert("RGB")
        draw = ImageDraw.Draw(screenshot)
        
        for result in results:
            x, y = result  # Unpack coordinates
            draw.rectangle([x, y, x + 1, y + 1], outline="red", width=1)
        
        # Show the modified screenshot with rectangles drawn
        print(time.time() - startTime)
        screenshot.show()

    return results  # Return the list of found points

# Output all location information
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

# Cut
def CutWood(treeType, X2, Y2):
    while True:
        _, _, _, _, angleOfApproach = allInfo(X2, Y2)
        try:
            treeLocs = highlight_color_on_screen(2501643, 5, region=(957, 110, 1834, 635), sections=10, drawLoc=False)

            sorted_trees = sorted(treeLocs, key=lambda loc: loc[0])
            leftTree = sorted_trees[0] # Leftmost tree
            rightTree = sorted_trees[-1] # Rightmost tree
            
            average_x = sum(loc[0] for loc in sorted_trees) / len(sorted_trees)
            middleTree = min(sorted_trees, key=lambda loc: abs(loc[0] - average_x))
        except:
            rotateCamera(angleOfApproach, limit=False)

        try:
            smooth_move(middleTree[0], middleTree[1])
            A, A1 = locateOnScreenRandom("TealIndicator.png")
        except:
            A, A1 = False, False

        if (A):
            autoit.mouse_click()
        else:
            try:
                smooth_move(leftTree[0], leftTree[1])
                A, A1 = locateOnScreenRandom("TealIndicator.png")
            except:
                A, A1 = False, False

            if (A):
                autoit.mouse_click()
            else:
                try:
                    smooth_move(rightTree[0], rightTree[1])
                    A, A1 = locateOnScreenRandom("TealIndicator.png")
                except:
                    A, A1 = False, False

                if (A):
                    autoit.mouse_click()
                else:
                    rotateCamera(angleOfApproach, limit=False)
        
        startTime = time.time()
        while True:
            try:
                if locateOnScreenRandom("WoodcuttingBooleanFalse.png", confidence=0.75):
                    if ((time.time() - startTime) > 5):
                        break
                    #print("Walking to Wood")
                    time.sleep(.01)
            except Exception as e:
                break
        
        while True:
            try:
                if locateOnScreenRandom("WoodcuttingBooleanTrue.png", confidence=0.75):
                    #print("Cutting Wood")
                    time.sleep(.01)
            except Exception as e:
                break

        break

# Bank
def BankWood(treeType, X2, Y2):
    while True:
        Distance, CompassX, CompassY, CompassWidth, angleOfApproach = allInfo(X2, Y2)
        if Distance < 5:
            try:
                print("Find Teller")
                if treeType == "Regular":
                    tellerLocs = highlight_color_on_screen(2564148, 5, region=(957, 110, 1834, 635), drawLoc=False)
                
                sortedTellers = sorted(tellerLocs, key=lambda loc: loc[0])
                leftTeller = sortedTellers[0] # Leftmost tree
                rightTeller = sortedTellers[-1] # Rightmost tree

                average_x = sum(loc[0] for loc in sortedTellers) / len(sortedTellers)
                middleTeller = min(sortedTellers, key=lambda loc: abs(loc[0] - average_x))
            except:
                rotateCamera(angleOfApproach, limit=False)
                continue
            
            try:
                smooth_move(middleTeller[0], middleTeller[1])
                A, A2 = locateOnScreenRandom("TalkToBanker.png")
            except:
                A, A2 = False, False

            try:
                B, B2 = locateOnScreenRandom("BankBooth.png")
            except:
                B, B2 = False, False

            if A or B:
                BankBool = True
            else:
                try:
                    smooth_move(leftTeller[0], leftTeller[1])
                    A, A2 = locateOnScreenRandom("TalkToBanker.png")
                except:
                    A, A2 = False, False

                try:
                    B, B2 = locateOnScreenRandom("BankBooth.png")
                except:
                    B, B2 = False, False
                
                if A or B:
                    BankBool = True
                else:
                    try:
                        smooth_move(rightTeller[0], rightTeller[1])
                        A, A2 = locateOnScreenRandom("TalkToBanker.png")
                    except:
                        A, A2 = False, False

                    try:
                        B, B2 = locateOnScreenRandom("BankBooth.png")
                    except:
                        B, B2 = False, False
                    
                    if A or B:
                        BankBool = True
                    else:
                        break
            if BankBool:
                print("Bank")
                autoit.mouse_click("right")
                time.sleep(random.uniform(.4, .6))
                RandomX, RandomY = locateOnScreenRandom("BankBanker.png")
                smooth_move(RandomX, RandomY)
                autoit.mouse_click("left")
                time.sleep(random.uniform(4,5))

                if treeType == "Regular":
                    points = list(pyautogui.locateAllOnScreen("Logs.png", confidence=0.35, region=(1663,379,257,300)))
                point = random.choice(points)
                x, y, w, h = point[0], point[1], point[2], point[3]
                RandomX = random.randrange(x, x + w)
                RandomY = random.randrange(y, y + h)
                smooth_move(RandomX, RandomY)

                autoit.mouse_click("left")
                time.sleep(random.uniform(.4, .6))
                autoit.send("{Esc}", mode=0)
                break
        elif Distance < 75:
            print("Short Run")
            correctPath(CompassX, CompassY, CompassWidth, angleOfApproach, Distance)
        else:
            setWorldMapPath("SouthBank")
            pathLoop()

# Bank, Cut, or Run?
def WoodCutter(treeType):
    if treeType == "Regular":
        X2, Y2 = 3164, 3403
        BankX, BankY = 3182, 3440
    while True:
        try:
            Distance, CompassX, CompassY, CompassWidth, angleOfApproach = allInfo(X2, Y2)

            if (autoit.pixel_get_color(1826, 612) == 7229226):
                print("Inventory is full")
                if str(treeType) == "Regular":
                    BankWood(treeType, BankX, BankY)
            else:
                if (Distance < 75) and (Distance > 10):
                    print("Short Run")
                    correctPath(CompassX, CompassY, CompassWidth, angleOfApproach, Distance)
                elif (Distance < 3000) and (Distance > 75):
                    print("Long Run")
                    setWorldMapPath(treeType)
                    pathLoop()
                else:
                    print("Cut Wood")
                    CutWood(treeType, X2, Y2)
            time.sleep(1)
        except Exception as e:
            print(e)

autoit.win_activate("RuneLite") # Bring Runescape Client to the Foreground
autoit.win_move("RuneLite", 856, 0, 1072, 686)  # Resize
os.chdir(os.path.dirname(os.path.abspath(__file__))) # Change Directory to the Folder this script is in

WoodCutter("Regular")