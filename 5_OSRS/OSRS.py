# pylint: disable=invalid-name,broad-exception-caught
import argparse
import math  # For mathematical operations.
import os  # For changing directories and file system interactions.
import random  # To introduce randomness into movements.
import statistics  # To calculate statistical means.
import time  # For controlling the timing of actions.
from enum import StrEnum
from typing import NamedTuple

import autoit  # To interact with the game window and environment.
import mouse  # To get current mouse position.
import numpy as np  # For handling array operations.
import pyautogui  # For capturing screen data and simulating mouse movements.
import pytesseract  # Used for Optical Character Recognition (OCR).
from PIL import ImageDraw  # For image processing and drawing.


# ===Classes and Containers====
class Point(NamedTuple):
    """
    A point in 2D space.
    """

    x: int
    y: int


class FractionalPoint(NamedTuple):
    """
    A point in 2D space, using floats.
    """

    x: float
    y: float


class Region(NamedTuple):
    """
    A region in 2D space, outlined by four points.
    """

    x1: int
    y1: int
    x2: int
    y2: int


class PointWithHeight(NamedTuple):
    """
    A point in space with an accompanying height, usually used for locating
    an object on the screen.
    """

    x: int
    y: int
    height: int


class CompassData(NamedTuple):
    """
    A representation of RuneScape's compass: its location on-screen, its size,
    the angle it's pointing to.
    """

    x: int
    y: int
    width: int
    angle: float


class LocationData(NamedTuple):
    """
    A container for data regarding a point in 2D-space relative to a given position.
    """

    distance: float
    compass_x: int
    compass_y: int
    compass_width: int
    compass_angle: float
    angle_of_approach: float


class Tree(StrEnum):
    """
    Where shall we chop?
    """

    REGULAR = "Regular"
    WILLOW = "Willow"
    # wat
    GRAND_EXCHANGE = "GrandExchange"
    SOUTH_BANK = "SouthBank"


# ======Utility Functions======


def smoothMove(x2: int | float, y2: int | float) -> None:
    """
    Smoothly moves the mouse from the current position to a target position (x2, y2).
    Incorporates random movement patterns to simulate human-like behavior.
    """
    try:
        x1, y1 = mouse.get_position()
        trig = random.randint(1, 4)
        if (abs(x2 - x1) > 750) or (abs(y2 - y1) > 750):
            amplitude = random.randint(75, 100)
            duration = random.uniform(0.75, 1)
        elif (abs(x2 - x1) > 350) or (abs(y2 - y1) > 500):
            amplitude = random.randint(50, 75)
            duration = random.uniform(0.5, 0.75)
        elif (abs(x2 - x1) > 75) or (abs(y2 - y1) > 75):
            amplitude = random.randint(25, 50)
            duration = random.uniform(0.5, 0.75)
        else:  # Very Short Movements Don't Arc Up/Down
            amplitude = 0
            trig = 5
            duration = random.uniform(0.25, 0.5)
        points = []
        num_points = int(duration * 75)
        for i in range(num_points + 1):
            ratio = i / num_points
            x = int(x1 + (x2 - x1) * ratio)
            if trig == 1:  # Sin Function w/ Sin Noise
                y_variation = int(
                    amplitude * math.sin(ratio * math.pi) + 0.2 * math.sin(30 * ratio)
                )
            elif trig == 2:  # Sin Function w/ Cos Noise
                y_variation = int(
                    amplitude * math.sin(ratio * math.pi)
                    + 0.2 * math.cos(30 * ratio + (math.pi / 2))
                )
            elif trig == 3:  # Cos Function w/ Sin Noise
                y_variation = int(
                    amplitude * math.sin(ratio * math.pi + math.pi)
                    + 0.2 * math.sin(30 * ratio)
                )
            elif trig == 4:  # Cos Function w/ Cos Noise
                y_variation = int(
                    amplitude * math.sin(ratio * math.pi + math.pi)
                    + 0.2 * math.cos(30 * ratio + (math.pi / 2))
                )
            elif trig == 5:  # Very Short Movements don't Arc Up/Down
                y_variation = 0
            else:
                raise ValueError(f"Unrecognized value for trig: {trig=}")
            y = int(y1 + (y2 - y1) * ratio + y_variation)
            points.append(Point(x, y))
        for i, point in enumerate(points):
            x, y = point
            mouse.move(x, y, absolute=True)
            middle_ratio = abs(0.5 - (i / num_points))
            sleep_duration = duration * (0.5 + 0.5 * middle_ratio) / len(points)
            time.sleep(sleep_duration)
        time.sleep(random.uniform(0.15, 0.35))
    except Exception as exc:
        print(f"smoothMove() Error: {exc}")


def calculateAngle(
    center: Point | FractionalPoint, point: Point | FractionalPoint
) -> float | None:
    """
    Calculates the angle between the center point and a target point.
    Returns the angle in degrees.
    """
    try:
        cx, cy = center
        px, py = point
        delta_x = px - cx
        delta_y = py - cy
        angle_radians = math.atan2(delta_y, delta_x)
        angle_degrees = math.degrees(angle_radians)
        angle_degrees = (angle_degrees + 90) % 360
        return angle_degrees
    except Exception as exc:
        print(f"calculateAngle() error: {exc}")
        return None


# TODO type for region?
def locateOnScreenRandom(fileName: str, confidence: float = 0.8, Region=None) -> Point:
    """
    Locate an image on the screen.
    Returns randomized X, Y coordinates within the found area.
    """
    try:
        fileName = ".\\Image Files\\" + fileName
        if Region:
            x, y, w, h = pyautogui.locateOnScreen(
                fileName, confidence=0.35, region=Region
            )
        else:
            x1, y1, x2, y2 = autoit.win_get_pos("RuneLite")
            x, y, w, h = pyautogui.locateOnScreen(
                fileName, confidence=confidence, region=(x1, y1, x2 - x1, y2 - y1)
            )

        return Point(random.randrange(x, x + w), random.randrange(y, y + h))
    except Exception as exc:
        print(f"Couldn't find the image {fileName} on screen: {exc}; returning (0, 0)")
        return Point(0, 0)


def highlightColorOnScreen(
    color: int,
    tolerance: int,
    region: Region,
    sections: int = 30,
    drawLoc: bool = False,
):
    """
    Find Color On Screen (Such as Tree Color)
    """
    try:
        if drawLoc:
            startTime = time.time()

        x1, y1, x2, y2 = region
        results = []
        width = x2 - x1
        height = y2 - y1
        sub_width: int = width // sections  # Divide into columns
        sub_height: int = height // sections  # Divide into rows

        # Loop through each sub-region
        for i in range(sections):
            for j in range(sections):
                sub_x1 = x1 + (j * sub_width)
                sub_y1 = y1 + (i * sub_height)
                # Adjust sub_x2 and sub_y2 to not exceed (x2, y2)
                sub_x2 = sub_x1 + sub_width if j < sections - 1 else x2
                sub_y2 = sub_y1 + sub_height if i < sections - 1 else y2

                try:
                    result = autoit.pixel_search(
                        sub_x1, sub_y1, sub_x2, sub_y2, color, tolerance
                    )
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

                    draw.rectangle(
                        [section_x1, section_y1, section_x2, section_y2],
                        outline="blue",
                        width=1,
                    )

            # Highlight found pixel locations as yellow dots
            for result in results:
                if result:  # Check if result is valid
                    x, y = result  # Unpack coordinates
                    draw.ellipse(
                        [x - 2, y - 2, x + 2, y + 2], fill="yellow", width=10
                    )  # Draw a yellow dot

            # Show the modified screenshot with rectangles and dots drawn
            screenshot.show()
            print("Time elapsed:", time.time() - startTime)
            time.sleep(100)

        return results  # Return the list of found points
    except Exception as exc:
        print(f"highlightColorOnScreen() Error: {exc}")


# ======Information Retrieval Functions======


def findLocation(drawLoc: bool = False) -> PointWithHeight | None:
    """
    Finds the location (X, Y, Height) of the player's character on the screen.
    Optionally draws the location box.
    """
    try:
        x, y, _, _ = pyautogui.locateOnScreen(
            ".\\Image Files\\LocationBox.png", confidence=0.75
        )
        x, y = int(x), int(y)
        if x:
            LocationText = pyautogui.screenshot(region=(x + 31, y, 98, 23))
            if drawLoc == True:
                LocationText.show()
            pytesseract.pytesseract.tesseract_cmd = r".\Tesseract-OCR\tesseract.exe"
            custom_config = r"--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789,"
            string = pytesseract.image_to_string(LocationText, config=custom_config)
            x, y, height = string.split("\n")[0].split(",")
            x, y, height = int(x), int(y), int(height)
        return PointWithHeight(x, y, height)
    except Exception as exc:
        print(f"findLocation() error: {exc}")
        return None


def readCompass() -> CompassData | None:
    """
    Reads the player's compass data from the screen.
    Returns CompassX, CompassY, CompassWidth, CompassAngle.
    """
    try:
        CompassX, CompassY, CompassWidth, CompassHeight = 1702, 28, 44, 44
        Compass = pyautogui.screenshot(
            region=(CompassX, CompassY, CompassWidth, CompassHeight)
        )
        XArray, YArray = [], []
        for x in range(CompassWidth):
            for y in range(CompassHeight):
                current_color = Compass.getpixel((x, y))
                if current_color == (49, 41, 29):
                    XArray.append(x)
                    YArray.append(y)
        CompassAngle: float
        if len(XArray) > 1:
            x_avg = statistics.mean(XArray)
            y_avg = statistics.mean(YArray)
            CompassAngle = (
                calculateAngle(
                    FractionalPoint((CompassWidth / 2), (CompassHeight / 2)),
                    FractionalPoint(x_avg, y_avg),
                )
                or 0.0
            )
        else:
            print("readCompass couldn't compute a compass angle!")
            CompassAngle = 0.0
        # NOTE: On an error, it's possible for the compass angle to come out as None.
        # Let's default to 0.0.
        return CompassData(CompassX, CompassY, CompassWidth, CompassAngle)
    except Exception as exc:
        print(f"readCompass() Error: {exc}")
        return None


def allInfo(X2: int, Y2: int) -> LocationData | None:
    """
    Output all location information
    """
    try:
        os.system("cls")  # Clear previous update
        if not (character_location := findLocation(drawLoc=False)):
            print("allInfo failed to find the character's location.")
            return None
        x, y, _ = character_location
        distance = math.sqrt((X2 - x) ** 2 + (Y2 - y) ** 2)
        if not (compass_data := readCompass()):
            print("allInfo failed to get any compass data.")
            return None
        compass_x, compass_y, compass_width, compass_angle = compass_data
        if not (direction_angle := calculateAngle(Point(0, 0), Point(X2 - x, y - Y2))):
            print("allInfo failed to find the direction angle.")
            return None
        angle_of_approach = (direction_angle - 360) + compass_angle
        info = LocationData(
            distance,
            compass_x,
            compass_y,
            compass_width,
            compass_angle,
            angle_of_approach,
        )

        print("Location: " + str(x) + ", " + str(y))
        print("Distance: " + str(distance))
        print("Angle of Player: " + str(round(compass_angle, 1)))
        print("Angle of Destination: " + str(round(direction_angle, 1)))
        print("Angle of Approach: " + str(round(angle_of_approach, 1)))

        return info
    except Exception as exc:
        print(f"allInfo() error: {exc}")
        return None


# ======Pathfinding and Movement Functions==========


def rotateCamera(angle: int | float, limit: bool = True) -> None:
    """
    Rotate the in-game camera by a certain angle.
    Optionally limits rotation to avoid small rotations
    """
    try:
        x = random.randint(1278, 1531)
        y = random.randint(300, 400)
        if angle < 0:
            angle = angle + 360

        if limit is True:
            top = 315
            bottom = 45
        else:
            top = 360
            bottom = 0
        if angle < 180 and angle > bottom:
            dragDistance = 278 * (angle // 90)
            smoothMove(x, y)
            autoit.mouse_down("middle")
            smoothMove(x + dragDistance, y)
        elif angle > 180 and angle < top:
            dragDistance = 278 * ((360 - angle) // 90)
            smoothMove(x, y)
            autoit.mouse_down("middle")
            smoothMove(x - dragDistance, y)
        autoit.mouse_up("middle")
    except Exception as exc:
        print(f"rotateCamera() Error: {exc}")


def setWorldMapPath(location: Tree) -> None:
    """
    Sets the world map path to a specific location.
    Clicks through the GUI to set the player's location on the world map.
    """
    try:
        RandomX, RandomY = locateOnScreenRandom("Globe.png")
        smoothMove(RandomX, RandomY)
        autoit.mouse_click("left")
        time.sleep(random.uniform(1, 1.25))
        RandomX, RandomY = locateOnScreenRandom("WorldMap.png")
        smoothMove(RandomX, RandomY)
        autoit.mouse_click("left")
        time.sleep(random.uniform(0.2, 0.4))
        if location == Tree.REGULAR:
            X1, Y1 = 1577, 407
        elif location == Tree.WILLOW:
            X1, Y1 = 1574, 413
        elif location == Tree.GRAND_EXCHANGE:
            X1, Y1 = 1579, 400
        elif location == Tree.SOUTH_BANK:
            X1, Y1 = 1578, 404
        else:
            raise ValueError(f"Unsupported location for world map pathing: {location}")

        smoothMove(X1, Y1)
        autoit.mouse_down("left")
        time.sleep(random.uniform(0.2, 0.4))
        autoit.mouse_up("left")
        time.sleep(random.uniform(0.5, 0.75))
        x, y = locateOnScreenRandom(location + ".png", confidence=0.6)
        smoothMove(x, y)
        autoit.mouse_click("right")
        time.sleep(random.uniform(0.5, 0.75))
        smoothMove(x + random.randint(-49, 43), y + random.randint(35, 48))
        autoit.mouse_click("left")
        time.sleep(random.uniform(0.5, 0.75))
        autoit.send("{Esc}", mode=0)
        time.sleep(random.uniform(1.5, 1.75))
    except Exception as exc:
        print(f"setWorldMapPath() Error: {exc}")


def correctPath(treeType: Tree, Info: LocationData) -> None:
    """
    Clicks towards a target using the minimap.
    Adjusts sleep duration based on the treeType
    """
    try:
        Distance, _, _, _, _, angleOfApproach = Info

        MinimapX, MinimapY, MinimapWidth, MinimapHeight = 1725, 35, 154, 154
        CenterX, CenterY = MinimapX + (MinimapWidth / 2), MinimapY + (MinimapHeight / 2)
        if Distance > 15:
            mapDistance = random.randint(66, 70)
        elif Distance > 10:
            mapDistance = random.randint(35, 40)
        else:
            mapDistance = random.randint(20, 25)
        dx = mapDistance * math.cos(math.radians(angleOfApproach - 90))
        dy = mapDistance * math.sin(math.radians(angleOfApproach - 90))
        smoothMove(CenterX + dx, CenterY + dy)
        autoit.mouse_click()
        startTime = time.time()
        rotateCamera(angleOfApproach)
        if autoit.pixel_get_color(1726, 160) == 15522407:  # If Running
            if treeType == Tree.WILLOW:
                time.sleep(9 - (time.time() - startTime))
            else:
                time.sleep(3 - (time.time() - startTime))
        else:
            if treeType == Tree.WILLOW:
                time.sleep(11 - (time.time() - startTime))
            else:
                time.sleep(7 - (time.time() - startTime))
    except Exception as exc:
        print(f"correctPath() Error {exc}")


def findPath() -> tuple[Point | None, float | None]:
    """
    Finds the pathway towards a location using the minimap.
    Evaluates the color on the minimap for pathfinding.
    """
    try:
        MinimapX, MinimapY, MinimapWidth, MinimapHeight = 1725, 35, 154, 154
        Minimap = pyautogui.screenshot(region=(MinimapX, MinimapY, 154, 154))
        compass_array = np.array(Minimap)
        target_color = (201, 132, 255)  # Pink Path
        XArray = []
        YArray = []

        # Define a safe zone distance from the edge to avoid clicks too close to the edge
        buffer_zone = 23  # Adjust this distance as needed

        for x in range(MinimapWidth):
            for y in range(MinimapHeight):
                current_color = tuple(compass_array[y, x])
                if current_color == target_color:
                    # Only accept colors that are inside the buffer zone
                    if (
                        x >= buffer_zone
                        and x <= MinimapWidth - buffer_zone - 1
                        and y >= buffer_zone
                        and y <= MinimapHeight - buffer_zone - 1
                    ):
                        XArray.append(x)
                        YArray.append(y)

        max_distance = 2000000
        min_distance = 10
        PathPoint = Point(0, 0)

        for x, y in zip(XArray, YArray):
            distance_to_edge = min(x, y, MinimapWidth - x - 1, MinimapHeight - y - 1)
            if distance_to_edge < max_distance and distance_to_edge > min_distance:
                max_distance = distance_to_edge
                PathPoint = Point(x + MinimapX, y + MinimapY)

        # Calculate the angle to the target path point from the Center
        PathAngle = calculateAngle(Point(MinimapX + 77, MinimapY + 77), PathPoint)
        return PathPoint, PathAngle

    except Exception:
        return None, None


def pathLoop(TreeX: int, TreeY: int) -> None:
    """
    Loop to continuously walk the path found by findPath().
    Simulates continuous movement towards the path until the task is completed.
    """
    try:
        while True:
            try:
                PathPoint, PathAngle = findPath()
                if not PathPoint:
                    raise ValueError("findPath returned no point.")
                if not PathAngle:
                    raise ValueError("findPath returned no angle.")
                smoothMove(PathPoint[0], PathPoint[1])
                autoit.mouse_click()
                startTime = time.time()
                time.sleep(random.uniform(0.4, 0.6))
                rotateCamera(PathAngle)
                if autoit.pixel_get_color(1726, 160) == 15522407:  # If Running
                    time.sleep(3 - (time.time() - startTime))
                else:
                    time.sleep(7 - (time.time() - startTime))
            except Exception:
                print(f"Path to ({TreeX}, {TreeY}) complete.")
                break
    except Exception as exc:
        print(f"pathLoop() Error: {exc}")


# ======Woodcutting TasK Functions==========


def cutWood(treeType: Tree, Info: LocationData):
    """
    Handles the woodcutting task for the player.
    Finds trees, moves to them, and cuts the trees
    """
    try:
        while True:
            _, _, _, _, _, angleOfApproach = Info

            try:
                if treeType == Tree.REGULAR:
                    treeLocs = highlightColorOnScreen(
                        2501643,
                        5,
                        region=Region(957, 110, 1834, 635),
                        sections=10,
                        drawLoc=False,
                    )
                elif treeType == Tree.WILLOW:
                    treeLocs = highlightColorOnScreen(
                        3555344,
                        1,
                        region=Region(957, 110, 1834, 635),
                        sections=10,
                        drawLoc=False,
                    )

                filtered_trees = [
                    loc
                    for loc in treeLocs
                    if 957 <= loc[0] <= 1834 and 110 <= loc[1] <= 635
                ]
                sorted_trees = sorted(filtered_trees, key=lambda loc: loc[0])
                leftTree = sorted_trees[0]  # Leftmost tree
                rightTree = sorted_trees[-1]  # Rightmost tree

                average_x = sum(loc[0] for loc in sorted_trees) / len(sorted_trees)
                middleTree = min(sorted_trees, key=lambda loc: abs(loc[0] - average_x))
            except Exception:
                print(f"Couldn't see a {treeType}; rotating.")
                rotateCamera(angleOfApproach, limit=False)

            smoothMove(middleTree[0], middleTree[1])
            A, _ = locateOnScreenRandom(
                "TealIndicator" + treeType + ".png", confidence=0.9
            )

            if A:
                autoit.mouse_click()
            else:
                smoothMove(leftTree[0], leftTree[1])
                A, _ = locateOnScreenRandom(
                    "TealIndicator" + treeType + ".png", confidence=0.9
                )

                if A:
                    autoit.mouse_click()
                else:
                    smoothMove(rightTree[0], rightTree[1])
                    A, _ = locateOnScreenRandom(
                        "TealIndicator" + treeType + ".png", confidence=0.9
                    )

                    if A:
                        autoit.mouse_click()
                    else:
                        rotateCamera(angleOfApproach, limit=False)
                        break

            startTime = time.time()
            while True:
                # Walking to Wood
                # print("Walking To Wood")
                A, _ = locateOnScreenRandom(
                    "WoodcuttingBooleanFalse.png", confidence=0.65
                )
                if A:
                    if (time.time() - startTime) > 5:
                        break
                    time.sleep(0.01)
                else:
                    break

            while True:
                # Cutting Wood
                # print("Cutting Wood")
                B, _ = locateOnScreenRandom(
                    "WoodcuttingBooleanTrue.png", confidence=0.65
                )
                if B:
                    time.sleep(0.01)
                else:
                    break
            break
    except Exception as exc:
        print(f"cutWood() Error: {exc}")


def bankWood(
    treeType: Tree, BankX: int, BankY: int, colorTeller, distanceLimit: int = 5
) -> None:
    """
    Banks the wood by interacting with the banker
    """
    try:
        while True:
            Info = allInfo(BankX, BankY)
            if not Info:
                raise ValueError(
                    "allInfo couldn't get me the location info for the bank at "
                    f"({BankX}, {BankY})."
                )
            Distance, _, _, _, _, angleOfApproach = Info

            if Distance < distanceLimit:
                try:
                    print("Find Teller")
                    x1, y1, x2, y2 = autoit.win_get_pos("RuneLite")
                    if treeType == "Regular":
                        tellerLocs = highlightColorOnScreen(
                            colorTeller,
                            1,
                            region=Region(x1, y1, x2, y2),
                            sections=10,
                            drawLoc=False,
                        )
                    elif treeType == "Willow":
                        tellerLocs = highlightColorOnScreen(
                            colorTeller,
                            1,
                            region=Region(x1, y1, x2, y2),
                            sections=10,
                            drawLoc=False,
                        )

                    filteredTellers = [
                        loc
                        for loc in tellerLocs
                        if x1 <= loc[0] <= x2 and y1 <= loc[1] <= y2
                    ]
                    sortedTellers = sorted(filteredTellers, key=lambda loc: loc[0])
                    leftTeller = sortedTellers[0]  # Leftmost tree
                    rightTeller = sortedTellers[-1]  # Rightmost tree

                    average_x = sum(loc[0] for loc in sortedTellers) / len(
                        sortedTellers
                    )
                    middleTeller = min(
                        sortedTellers, key=lambda loc: abs(loc[0] - average_x)
                    )
                except Exception:
                    print("Couldn't see a teller. Rotating camera.")
                    rotateCamera(angleOfApproach, limit=False)
                    continue

                smoothMove(middleTeller[0], middleTeller[1])
                A, _ = locateOnScreenRandom("TalkToBanker.png")
                B, _ = locateOnScreenRandom("BankBooth.png")

                BankBool = False
                if A or B:
                    BankBool = True
                else:
                    smoothMove(leftTeller[0], leftTeller[1])
                    A, _ = locateOnScreenRandom("TalkToBanker.png")
                    B, _ = locateOnScreenRandom("BankBooth.png")

                    if A or B:
                        BankBool = True
                    else:
                        smoothMove(rightTeller[0], rightTeller[1])
                        A, _ = locateOnScreenRandom("TalkToBanker.png")
                        B, _ = locateOnScreenRandom("BankBooth.png")

                        if A or B:
                            BankBool = True

                if BankBool:
                    print("Bank")
                    autoit.mouse_click("left")
                    time.sleep(random.uniform(0.3, 0.5))

                    breakout = 0
                    bankOpenTimer = time.time()
                    while True:
                        A, B = locateOnScreenRandom("BankOpened.png")
                        if A:
                            break
                        if time.time() - bankOpenTimer > 10:
                            breakout = 1
                            break

                    # If opening the bank timed out, press Esc and Break the Larger While Loop
                    if breakout:
                        autoit.send("{Esc}", mode=0)
                        break

                    points = list(
                        pyautogui.locateAllOnScreen(
                            ".\\Image Files\\" + str(treeType) + "Logs.png",
                            confidence=0.6,
                            region=(1663, 379, 257, 300),
                        )
                    )
                    point = random.choice(points)
                    x, y, w, h = point[0], point[1], point[2], point[3]
                    x, y = int(x), int(y)
                    RandomX = random.randrange(x, x + w)
                    RandomY = random.randrange(y, y + h)

                    drawLoc = False
                    if drawLoc:
                        # Get the screenshot and draw rectangles for each found point
                        screenshot = pyautogui.screenshot(
                            region=(1663, 379, 257, 300)
                        ).convert("RGB")
                        draw = ImageDraw.Draw(screenshot)

                        for point in points:
                            x, y, w, h = point[0], point[1], point[2], point[3]
                            draw.rectangle([x, y, x + 1, y + 1], outline="red", width=1)
                        # Show the modified screenshot with rectangles drawn
                        screenshot.show()
                        time.sleep(100)
                    smoothMove(RandomX, RandomY)

                    autoit.mouse_click("left")
                    time.sleep(random.uniform(0.4, 0.6))
                    autoit.send("{Esc}", mode=0)
                    break
                else:
                    rotateCamera(angleOfApproach, limit=False)
            elif Distance < 75:
                print("Short Run")
                correctPath(treeType, Info)
            else:
                if treeType == "Regular":
                    setWorldMapPath(Tree.SOUTH_BANK)
                elif treeType == "Willow":
                    setWorldMapPath(Tree.WILLOW)
                pathLoop(BankX, BankY)
    except Exception as exc:
        print(f"bankWood() Error: {exc}")


def dropWood(treeType: Tree) -> None:
    """
    Drops the wood if bankBool is set to False (Power Leveling)
    """
    points = list(
        pyautogui.locateAllOnScreen(
            ".\\Image Files\\" + str(treeType) + "Logs.png",
            confidence=0.4,
            region=(1663, 379, 257, 300),
        )
    )

    filtered_points: list[tuple[int, ...]] = []

    # Filtering points to avoid overlaps
    for point in points:
        x, y, w, h = point[0], point[1], point[2], point[3]

        # Check if any points in filtered_points are too close (X coordinate + width + 15)
        if not any(
            px + pw + 15 > x and abs(py - y) <= 15
            for (px, py, pw, ph) in filtered_points
        ):
            filtered_points.append((x, y, w, h))

    for point in filtered_points:
        x, y, w, h = point
        x, y = int(x), int(y)
        RandomX = random.randrange(x, x + w)
        RandomY = random.randrange(y, y + h)
        smoothMove(RandomX, RandomY)
        autoit.mouse_click("left")
        time.sleep(random.uniform(0.1, 0.3))


def woodCutter(treeType: Tree, bankBool: bool = True):
    """
    Bank, Cut, or Run?
    """
    if treeType == Tree.REGULAR:
        cutting = True
        TreeX, TreeY = 3164, 3403
        BankX, BankY = 3182, 3440
        colorLogs = 7229226
        colorTeller = 2564148
        distanceLimit = 5
    elif treeType == Tree.WILLOW:
        cutting = True
        TreeX, TreeY = 3087, 3232
        BankX, BankY = 3094, 3243
        colorLogs = 4405779
        colorTeller = 5261636
        distanceLimit = 3
    elif treeType == Tree.GRAND_EXCHANGE:
        cutting = False
        TreeX, TreeY = 3164, 3486
        distanceLimit = 5
        colorLogs = 0000000
    else:
        raise ValueError(f"Unsupported tree type for wood cutter: {treeType}")

    while True:
        try:
            Info = allInfo(TreeX, TreeY)
            if not Info:
                raise ValueError(
                    "woodCutter couldn't get location info for targeted object!"
                )
            (
                Distance,
                CompassX,
                CompassY,
                CompassWidth,
                CompassAngle,
                angleOfApproach,
            ) = Info
            if not Info:
                raise ValueError("allInfo couldn't get location data for me.")
            PathPoint, _ = findPath()
            if PathPoint:  # Previous Path On Map Exists
                pathLoop(TreeX, TreeY)
            else:
                if autoit.pixel_get_color(1826, 612) == colorLogs:
                    print("Inventory is full")
                    if bankBool:
                        bankWood(
                            treeType,
                            # TODO these are missing for grand exchange. Why?
                            BankX,
                            BankY,
                            colorTeller,
                            distanceLimit=distanceLimit,
                        )
                    else:
                        dropWood(treeType)
                else:
                    if (Distance < 75) and (Distance > distanceLimit):
                        print("Short Run")
                        correctPath(treeType, Info)
                    elif (Distance < 100000) and (Distance > 75):
                        print("Long Run")
                        setWorldMapPath(treeType)
                        pathLoop(TreeX, TreeY)
                    else:
                        if cutting:
                            print("Cut Wood")
                            cutWood(treeType, Info)
                        else:
                            break
            time.sleep(1)
        except Exception as e:
            pass


def main() -> None:
    """
    Run the bot with the selected parameters.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tree-type",
        default=Tree.REGULAR,
        required=True,
        choices=Tree,
        help="The kind of tree to chop.",
    )
    parser.add_argument(
        "-p",
        "--power-leveling",
        action="store_false",
        help="Don't bank our logs. Just power level.",
    )
    args = parser.parse_args()
    autoit.win_activate("RuneLite")  # Bring Runescape Client to the Foreground
    autoit.win_move("RuneLite", 856, 0, 1072, 686)  # Resize/Move
    os.chdir(
        os.path.dirname(os.path.abspath(__file__))
    )  # Change Directory to the Folder this script is in
    woodCutter(treeType=args.tree_type, bankBool=args.power_leveling)


# Cut Willows in Draynor
# woodCutter(Tree.WILLOW)

# Cut Willows in Draynor and Drop the Logs
# woodCutter(Tree.WILLOW, bankBool = False)

# Cut Regular Logs South of the GE
# woodCutter(Tree.REGULAR)

# Walk to the GE ("cutting" is False so it will end the script at the GE)
# woodCutter("GrandExchange")
