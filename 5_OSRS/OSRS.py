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

# Smoothly moves the mouse from the current position to a target position (x2, y2).
# Incorporates random movement patterns to simulate human-like behavior.
def smooth_move(x2, y2):
    try:
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
            y_variation = 0
            duration = random.uniform(0.25, .5)
        points = []
        num_points = int(duration * 75)
        trig = random.randint(1, 4)
        for i in range(num_points + 1):
            ratio = i / num_points
            x = int(x1 + (x2 - x1) * ratio)
            if trig == 1:
                y_variation = int(amplitude * math.sin(ratio * math.pi) + .2 * math.sin(30 * ratio))
            elif trig == 2:
                y_variation = int(amplitude * math.sin(ratio * math.pi) + .2 * math.cos(30 * ratio + (math.pi / 2)))
            elif trig == 3:
                y_variation = int(amplitude * math.sin(ratio * math.pi + math.pi) + .2 * math.sin(30 * ratio))
            elif trig == 4:
                y_variation = int(amplitude * math.sin(ratio * math.pi + math.pi) + .2 * math.cos(30 * ratio + (math.pi / 2)))
            elif trig == 5:
                y_variation = 0 
            y = int(y1 + (y2 - y1) * ratio + y_variation)
            points.append((x, y))
        for i, point in enumerate(points):
            x, y = point
            mouse.move(x, y, absolute=True)
            middle_ratio = abs(0.5 - (i / num_points))
            sleep_duration = duration * (0.5 + 0.5 * middle_ratio) / len(points)
            time.sleep(sleep_duration)
        time.sleep(random.uniform(.15, .35))
    except:
        print("smooth_move() Error")

# Finds the location (X, Y, Height) of the player's character on the screen.
# Optionally draws the location.
def findLocation(drawLoc = False):
    try:
        X1, Y1, X2, Y2 = autoit.win_get_pos("RuneLite")
        x, y, w, h = pyautogui.locateOnScreen(".\\Image Files\\LocationBox.png", confidence=.6, region=(X1, Y1, X2-X1, Y2-Y1))
        x, y = int(x), int(y)
        if x:
            LocationText = pyautogui.screenshot(region=(x + 28, y, 98, 20))
            if drawLoc == True:
                LocationText.show()
            pytesseract.pytesseract.tesseract_cmd = r".\Tesseract-OCR\tesseract.exe"
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789,'
            string = pytesseract.image_to_string(LocationText, config=custom_config)
            X, Y, Height = string.split("\n")[0].split(",")
            X, Y, Height = int(X), int(Y), int(Height)
        return X, Y, Height
    except Exception as e:
        print("findLocation() error")

# Reads the player's compass data from the screen.
# Returns CompassX, CompassY, CompassWidth, CompassAngle.
def readCompass():
    try:
        X1, Y1, X2, Y2 = autoit.win_get_pos("RuneLite")
        CompassX, CompassY, CompassWidth, CompassHeight = pyautogui.locateOnScreen(".\\Image Files\\" + "Compass.png", confidence=0.6, region=(X1, Y1, X2-X1, Y2-Y1))
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
    except:
        print("readCompass() Error")

# Calculates the angle between the center point and a target point.
# Returns the angle in degrees.
def calculateAngle(center, point):
    try:
        cx, cy = center
        px, py = point
        delta_x = px - cx
        delta_y = py - cy
        angle_radians = math.atan2(delta_y, delta_x)
        angle_degrees = math.degrees(angle_radians)
        angle_degrees = (angle_degrees + 90) % 360
        return angle_degrees
    except Exception as e:
        print("calculateAngle() error")

# Sets the world map path to a specific location.
# Clicks through the GUI to set the player's location on the world map.
def setWorldMapPath(location):
    try:
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
            X1, Y1 = 1575, 404
        elif location == "Willow":
            X1, Y1 = 1574, 413
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
        time.sleep(random.uniform(1.5, 1.75))
    except:
        print("setWorldMapPath() Error")

# Locate an image on the screen randomly.
# Returns randomized X, Y coordinates within the found area.
def locateOnScreenRandom(fileName, confidence=0.8, Region=None):
    try:
        fileName = ".\\Image Files\\" + fileName
        if Region:
            x, y, w, h = pyautogui.locateOnScreen(fileName, confidence=0.35, region=Region)
        else:
            x1,y1,x2,y2 = autoit.win_get_pos("RuneLite")
            x, y, w, h = pyautogui.locateOnScreen(fileName, confidence=confidence, region=(x1,y1,x2-x1,y2-y1))
        RandomX = random.randrange(x, x + w)
        RandomY = random.randrange(y, y + h)
        return RandomX, RandomY
    except:
        return False, False

# Rotate the in-game camera by a certain angle.
# Optionally limits rotation to avoid sharp turns.
def rotateCamera(angle, limit=True):
    try:
        origX, origY = autoit.mouse_get_pos()
        x = random.randint(1278, 1531)
        y = random.randint(300, 400)
        if angle < 0:
            angle = angle + 360

        if limit == True:
            top = 315
            bottom = 45
        elif limit == False:
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
    except:
        print("rotateCamera() Error")

# Clicks towards a target using the minimap.
# Adjusts direction based on the target type (tree).
def correctPath(treeType, Info):
    try:
        Distance, CompassX, CompassY, CompassWidth, CompassAngle, angleOfApproach = unpackInfo(Info)

        MinimapX, MinimapY = int(CompassX + (CompassWidth / 2) + 1), int(CompassY + 7)
        Minimap = pyautogui.screenshot(region=(MinimapX, MinimapY, 154, 154))
        CenterX, CenterY = MinimapX + 77, MinimapY + 77
        if Distance > 15:
            mapDistance = random.randint(66, 70)
        elif Distance > 10:
            mapDistance = random.randint(35, 40)
        elif Distance > 0:
            mapDistance = random.randint(20, 25)
        dx = mapDistance * math.cos(math.radians(angleOfApproach - 90))
        dy = mapDistance * math.sin(math.radians(angleOfApproach - 90))
        smooth_move(CenterX + dx, CenterY + dy)
        autoit.mouse_click()
        startTime = time.time()
        rotateCamera(angleOfApproach)
        if (autoit.pixel_get_color(1734, 157) == 12819969):
            if (treeType == "Regular"):
                time.sleep(3 - (time.time() - startTime))
            elif (treeType == "Willow"):
                time.sleep(9 - (time.time() - startTime))
            else:
                time.sleep(3 - (time.time() - startTime))
        else:
            if (treeType == "Regular"):
                time.sleep(7 - (time.time() - startTime))
            elif (treeType == "Willow"):
                time.sleep(11 - (time.time() - startTime))
            else:
                time.sleep(7 - (time.time() - startTime))
    except: 
        print("correctPath() Error")

# Finds the pathway towards a location using the minimap.
# Evaluates the color on the minimap for pathfinding.
def findPath(Info):
    try:
        Distance, CompassX, CompassY, CompassWidth, CompassAngle, angleOfApproach = unpackInfo(Info)
        MinimapX, MinimapY = int(CompassX + (CompassWidth / 2) + 1), int(CompassY + 7)
        Minimap = pyautogui.screenshot(region=(MinimapX, MinimapY, 154, 154))
        width = Minimap.width
        height = Minimap.height
        compass_array = np.array(Minimap)
        target_color = (201, 132, 255)
        XArray = []
        YArray = []
        
        # Define a safe zone distance from the edge to avoid clicks too close to the edge
        buffer_zone = 23  # Adjust this distance as needed

        for x in range(width):
            for y in range(height):
                current_color = tuple(compass_array[y, x])
                if current_color == target_color:
                    # Only accept colors that are not within the buffer zone from the edges
                    if x >= buffer_zone and x <= width - buffer_zone - 1 and \
                       y >= buffer_zone and y <= height - buffer_zone - 1:
                        XArray.append(x)
                        YArray.append(y)

        max_distance = 2000000
        min_distance = 10
        closest_pixel = None
        
        for x, y in zip(XArray, YArray):
            distance_to_edge = min(x, y, width - x - 1, height - y - 1)
            if distance_to_edge < max_distance and distance_to_edge > min_distance:
                max_distance = distance_to_edge
                PathPoint = (x + MinimapX, y + MinimapY)
                
        # Calculate the angle to the target path point
        PathAngle = calculateAngle((MinimapX + 77, MinimapY + 77), PathPoint)  # Center coordinates
        return PathPoint, PathAngle
        
    except Exception as e:
        print(f"findPath() Error: {e}")

# Loop to continuously walk the path found by findPath().
# Simulates continuous movement towards the path until the task is completed.
def pathLoop(treeType, TreeX, TreeY):
    try:
        while True:
            Info = allInfo(TreeX, TreeY)
            Distance, CompassX, CompassY, CompassWidth, CompassAngle, angleOfApproach = unpackInfo(Info)

            try:
                PathPoint, PathAngle = findPath(Info)
                smooth_move(PathPoint[0], PathPoint[1])
                autoit.mouse_click()
                startTime = time.time()
                time.sleep(random.uniform(.4, .6))
                rotateCamera(PathAngle)
                if (autoit.pixel_get_color(1734, 157) == 12819969):
                    if (treeType == "Regular"):
                        time.sleep(3 - (time.time() - startTime))
                    elif (treeType == "Willow"):
                        time.sleep(3 - (time.time() - startTime))
                    else:
                        time.sleep(3 - (time.time() - startTime))
                else:
                    if (treeType == "Regular"):
                        time.sleep(7 - (time.time() - startTime))
                    elif (treeType == "Willow"):
                        time.sleep(7 - (time.time() - startTime))
                    else:
                        time.sleep(7 - (time.time() - startTime))
            except:
                print("Path Complete")
                break
    except:
        print("pathLoop() Error")

# Find Color On Screen (Such as Tree Color)
def highlight_color_on_screen(color, tolerance, region, sections=30, drawLoc=False):
    try:
        if drawLoc:
            startTime = time.time()
            
        x1, y1, x2, y2 = region
        results = []
        width = x2 - x1
        height = y2 - y1
        sub_width = width // sections  # Divide into columns
        sub_height = height // sections  # Divide into rows
        
        # Loop through each sub-region
        for i in range(sections):
            for j in range(sections):
                sub_x1 = x1 + (j * sub_width)
                sub_y1 = y1 + (i * sub_height)
                # Adjust sub_x2 and sub_y2 to not exceed (x2, y2)
                sub_x2 = sub_x1 + sub_width if j < sections - 1 else x2
                sub_y2 = sub_y1 + sub_height if i < sections - 1 else y2
                
                try:
                    result = autoit.pixel_search(sub_x1, sub_y1, sub_x2, sub_y2, color, tolerance)
                    # Check if result is within the defined region
                    if result:  # Make sure result is valid and not None
                        x, y = result
                        # Only append valid results within the designated region
                        if x1 <= x <= x2 and y1 <= y <= y2:
                            results.append(result)  # Append found point to results
                except Exception as e:
                    continue

        if drawLoc:
            # Get the screenshot and draw rectangles for each section
            screenshot = pyautogui.screenshot().convert("RGB")
            draw = ImageDraw.Draw(screenshot)

            # Draw blue rectangles around the sections
            for i in range(sections):
                for j in range(sections):
                    section_x1 = x1 + (j * sub_width)
                    section_y1 = y1 + (i * sub_height)
                    section_x2 = section_x1 + sub_width if j < sections - 1 else x2
                    section_y2 = section_y1 + sub_height if i < sections - 1 else y2
                    
                    draw.rectangle([section_x1, section_y1, section_x2, section_y2], outline="blue", width=1)

            # Highlight found pixel locations as yellow dots
            for result in results:
                if result:  # Check if result is valid
                    x, y = result  # Unpack coordinates
                    draw.ellipse([x-2, y-2, x+2, y+2], fill="yellow", width=10)  # Draw a yellow dot
                    
            # Show the modified screenshot with rectangles and dots drawn
            screenshot.show()
            print("Time elapsed:", time.time() - startTime)
            time.sleep(100)

        return results  # Return the list of found points
    except Exception as e:
        print("highlight_color_on_screen() Error:", e)

# Output all location information
def allInfo(X2, Y2):
    try:
        Info = []
        #os.system('cls')
        X, Y, Height = findLocation(drawLoc=False)
        print("Location: " + str(X) + ", " + str(Y))

        Distance = math.sqrt((X2 - X) ** 2 + (Y2 - Y) ** 2)
        print("Distance: " + str(Distance))
        Info.append(Distance)

        CompassX, CompassY, CompassWidth, CompassAngle = readCompass()
        print("CompassX: " + str(CompassX) + " " + "CompassY: " + str(CompassY))
        print("Angle of Player: " + str(round(CompassAngle, 1)))
        Info.append(CompassX)
        Info.append(CompassY)
        Info.append(CompassWidth)
        Info.append(CompassAngle)

        DirectionAngle = calculateAngle((0, 0), (X2 - X, Y - Y2))
        print("Angle of Destination: " + str(round(DirectionAngle, 1)))

        angleOfApproach = (DirectionAngle - 360) + CompassAngle
        Info.append(angleOfApproach)
        print("Angle of Approach: " + str(round(angleOfApproach, 1)))

        return Info
    except Exception as e:
        print("allInfo() error")

# Unpack all location information
def unpackInfo(Info):
    Distance = Info[0]
    CompassX = Info[1]
    CompassY = Info[2]
    CompassWidth = Info[3]
    CompassAngle = Info[4]
    angleOfApproach = Info[5]
    return Distance, CompassX, CompassY, CompassWidth, CompassAngle,  angleOfApproach

# Handles the woodcutting task for the player.
# Finds trees, moves to them, and cuts the trees
def cutWood(treeType, Info):
    try:
        while True:
            Distance, CompassX, CompassY, CompassWidth, CompassAngle, angleOfApproach = unpackInfo(Info)

            try:
                if (treeType == "Regular"):
                    treeLocs = highlight_color_on_screen(2501643, 5, region=(957, 110, 1834, 635), sections=10, drawLoc=False)
                elif (treeType == "Willow"):
                    treeLocs = highlight_color_on_screen(3555344, 1, region=(957, 110, 1834, 635), sections=10, drawLoc=False)
                
                filtered_trees = [loc for loc in treeLocs if 957 <= loc[0] <= 1834 and 110 <= loc[1] <= 635]
                sorted_trees = sorted(filtered_trees, key=lambda loc: loc[0])
                leftTree = sorted_trees[0] # Leftmost tree
                rightTree = sorted_trees[-1] # Rightmost tree
                
                average_x = sum(loc[0] for loc in sorted_trees) / len(sorted_trees)
                middleTree = min(sorted_trees, key=lambda loc: abs(loc[0] - average_x))
            except:
                rotateCamera(angleOfApproach, limit=False)

            smooth_move(middleTree[0], middleTree[1])
            A, A1 = locateOnScreenRandom("TealIndicator" + treeType + ".png")

            if (A):
                autoit.mouse_click()
            else:
                smooth_move(leftTree[0], leftTree[1])
                A, A1 = locateOnScreenRandom("TealIndicator" + treeType + ".png")

                if (A):
                    autoit.mouse_click()
                else:
                    smooth_move(rightTree[0], rightTree[1])
                    A, A1 = locateOnScreenRandom("TealIndicator" + treeType + ".png")

                    if (A):
                        autoit.mouse_click()
                    else:
                        rotateCamera(angleOfApproach, limit=False)
                        break

            startTime = time.time()
            while True:
                # Walking to Wood
                # print("Walking To Wood")
                A, A1 = locateOnScreenRandom("WoodcuttingBooleanFalse.png", confidence=0.7)
                if A:
                    if ((time.time() - startTime) > 5):
                        break
                    time.sleep(.01)
                else: 
                    break
            
            while True:
                # Cutting Wood
                # print("Cutting Wood")
                B, B1 = locateOnScreenRandom("WoodcuttingBooleanTrue.png", confidence=0.7)
                if B:
                    time.sleep(.01)
                else:
                    break
            break
    except:
        print("cutWood() Error")

# Banks the cut wood by interacting with the banker
def bankWood(treeType, BankX, BankY, colorTeller, distanceLimit=5):
    try:
        while True:
            Info = allInfo(BankX, BankY)
            Distance, CompassX, CompassY, CompassWidth, CompassAngle, angleOfApproach = unpackInfo(Info)

            if Distance < distanceLimit:
                try:
                    print("Find Teller")
                    x1,y1,x2,y2 = autoit.win_get_pos("RuneLite")
                    if treeType == "Regular":
                        tellerLocs = highlight_color_on_screen(colorTeller, 1, region=(x1, y1, x2, y2),sections = 10, drawLoc=False)
                    elif treeType == "Willow":
                        tellerLocs = highlight_color_on_screen(colorTeller, 1, region=(x1, y1, x2, y2), sections = 10, drawLoc=False)

                    filteredTellers = [loc for loc in tellerLocs if x1 <= loc[0] <= x2 and y1 <= loc[1] <= y2]
                    sortedTellers = sorted(filteredTellers, key=lambda loc: loc[0])
                    leftTeller = sortedTellers[0] # Leftmost tree
                    rightTeller = sortedTellers[-1] # Rightmost tree

                    average_x = sum(loc[0] for loc in sortedTellers) / len(sortedTellers)
                    middleTeller = min(sortedTellers, key=lambda loc: abs(loc[0] - average_x))
                except:
                    rotateCamera(angleOfApproach)
                    continue
                
                smooth_move(middleTeller[0], middleTeller[1])
                A, A2 = locateOnScreenRandom("TalkToBanker.png")
                B, B2 = locateOnScreenRandom("BankBooth.png")
                
                BankBool = False
                if A or B:
                    BankBool = True
                else:
                    smooth_move(leftTeller[0], leftTeller[1])
                    A, A2 = locateOnScreenRandom("TalkToBanker.png")
                    B, B2 = locateOnScreenRandom("BankBooth.png")
                    
                    if A or B:
                        BankBool = True
                    else:
                        smooth_move(rightTeller[0], rightTeller[1])
                        A, A2 = locateOnScreenRandom("TalkToBanker.png")
                        B, B2 = locateOnScreenRandom("BankBooth.png")
                        
                        if A or B:
                            BankBool = True

                if BankBool:
                    print("Bank")
                    autoit.mouse_click("right")
                    time.sleep(random.uniform(.4, .6))
                    RandomX, RandomY = locateOnScreenRandom("BankBanker.png")
                    smooth_move(RandomX, RandomY)
                    autoit.mouse_click("left")
                    time.sleep(random.uniform(4,5))

                    breakout = 0
                    while True:
                        bankOpenTimer = time.time()
                        A, B = locateOnScreenRandom("BankOpened.png")
                        if (A):
                            break
                        if (time.time() - bankOpenTimer > 10):
                            breakout = 1
                            break

                    # If opening the bank timed out, press Esc and Break the Larger While Loop
                    if (breakout):
                        autoit.send("{Esc}", mode=0)
                        break

                    if treeType == "Regular":
                        points = list(pyautogui.locateAllOnScreen(".\\Image Files\\" + "Logs.png", confidence=0.4, region=(1663,379,257,300)))
                    elif treeType == "Willow":
                        points = list(pyautogui.locateAllOnScreen(".\\Image Files\\" + "WillowLogs.png", confidence=0.4, region=(1663,379,257,300)))
                    point = random.choice(points)
                    x, y, w, h = point[0], point[1], point[2], point[3]
                    x, y = int(x), int(y)
                    RandomX = random.randrange(x, x + w)
                    RandomY = random.randrange(y, y + h)

                    drawLoc = False
                    if drawLoc:
                        # Get the screenshot and draw rectangles for each found point
                        screenshot = pyautogui.screenshot(region=(1663,379,257,300)).convert("RGB")
                        draw = ImageDraw.Draw(screenshot)
                        
                        for point in points:
                            x, y, w, h = point[0], point[1], point[2], point[3]
                            draw.rectangle([x, y, x + 1, y + 1], outline="red", width=1)
                        
                        # Show the modified screenshot with rectangles drawn
                        screenshot.show()
                        time.sleep(100)
                        print(time.time() - startTime)
                    smooth_move(RandomX, RandomY)

                    autoit.mouse_click("left")
                    time.sleep(random.uniform(.4, .6))
                    autoit.send("{Esc}", mode=0)
                    break
                else:
                    rotateCamera(angleOfApproach)
            elif Distance < 75:
                print("Short Run")
                correctPath(treeType, Info)
            else:
                if treeType == "Regular":
                    setWorldMapPath("SouthBank")
                elif treeType == "Willow":
                    setWorldMapPath("Willow")
                pathLoop(treeType, BankX, BankY)
    except:
        print("bankWood() Error")

# Bank, Cut, or Run?
def woodCutter(treeType):
    if treeType == "Regular":
        cutting = True
        TreeX, TreeY = 3164, 3403
        BankX, BankY = 3182, 3440
        colorLogs = 7229226
        colorTeller = 2564148
        distanceLimit = 5
    if treeType == "Willow":
        cutting = True
        TreeX, TreeY = 3087, 3232
        BankX, BankY = 3094, 3243
        colorLogs = 4405779
        colorTeller = 5261636
        distanceLimit = 3
    if treeType == "GrandExchange":
        cutting = False
        TreeX, TreeY = 3164, 3486
        distanceLimit = 5
        colorLogs = 0000000

    while True:
        try:
            Info = allInfo(TreeX, TreeY)
            Distance, CompassX, CompassY, CompassWidth, CompassAngle, angleOfApproach = unpackInfo(Info)

            if (autoit.pixel_get_color(1826, 612) == colorLogs):
                print("Inventory is full")
                bankWood(treeType, BankX, BankY, colorTeller, distanceLimit=distanceLimit)
            else:
                if (Distance < 75) and (Distance > 10):
                    print("Short Run")
                    correctPath(treeType, Info)
                elif (Distance < 100000) and (Distance > 75):
                    print("Long Run")
                    setWorldMapPath(treeType)
                    pathLoop(treeType, TreeX, TreeY)
                else:
                    if cutting:
                        print("Cut Wood")
                        cutWood(treeType, Info)
                    else:
                        break
            time.sleep(1)
        except Exception as e:
            pass

autoit.win_activate("RuneLite") # Bring Runescape Client to the Foreground
autoit.win_move("RuneLite", 856, 0, 1072, 686)  # Resize
os.chdir(os.path.dirname(os.path.abspath(__file__))) # Change Directory to the Folder this script is in

# woodCutter("Regular")
woodCutter("Willow")
# woodCutter("GrandExchange")
