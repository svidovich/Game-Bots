import autoit
import pyautogui
import time
import os
import random
import math
import functools
import operator
from PIL import ImageChops

# Bring WoW Client to the Foreground
autoit.win_activate("World of Warcraft")

# Change Directory to the Folder this script is in
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Prevents an error if you close the bot before removing the last Bobber
try:
    os.remove("BobberLast.png")
except Exception as e:
    print("No leftover bobber image")

# Function to find the numerical difference between 2 images
def rmsdiff(im1, im2):
    h = ImageChops.difference(im1, im2).histogram()
    return math.sqrt(functools.reduce(operator.add, map(lambda h, i: h*(i**2), h, range(256))) / (float(im1.size[0]) * im1.size[1]))

LastCast = time.time() - 20  # Set a timer that is ready to cast
LastBait = time.time() - 600 # Set a timer that is ready to bait the hook

# Loop until broken
while True:
    try:
        # Screenshot only/right monitor
        Screen = pyautogui.screenshot(region=(0, 0, 1920, 1080))
        Screen.save("Screen.png")

        # Check for bait expiration
        if (time.time() - LastBait > 600):
            print("Bait Expired")
            autoit.control_send("World of Warcraft", "", "{3}", mode=0) # Press Bait
            time.sleep(random.random()) # Sleeps for a random duration (Between 0 and 1)
            autoit.control_send("World of Warcraft", "", "{2}", mode=0) # Press Fishing Pole
            LastBait = time.time()
            time.sleep(2) # Wait for bait to finish

        # If it's been 20 seconds, cast a new line
        if (time.time() - LastCast > 20):
            print("Time exceeded fishing timer")
            autoit.control_send("World of Warcraft", "", "{1}", mode=0) # Cast Line
            LastCast = time.time()
            time.sleep(2) # Wait for previous bobber to disappear

        # Monitor the bobber for a splash
        BobberX, BobberY, BobberWidth, BobberHeight = pyautogui.locateOnScreen("Bobber.png", confidence=0.65)
        # If a Bobber is Found
        if BobberX:
            print(f"Watching Bobber at ({BobberX}, {BobberY})")
            # Change values to basic integers
            BobberX, BobberY = int(BobberX), int(BobberY) 
            while True:
                # If it's been 20 seconds, cast a new line
                if (time.time() - LastCast > 20):
                    print("Time exceeded fishing timer")
                    LastCast = time.time()
                    autoit.control_send("World of Warcraft", "", "{1}", mode=0) # Cast Line
                    time.sleep(2) # Wait for previous bobber to disappear
                    break # Escape the While Loop that is watching the bobber

                # Screenshot of a small area around the bobber
                image = pyautogui.screenshot(region=(BobberX, BobberY, BobberWidth, BobberHeight))
                image.save("BobberCurrent.png")
                time.sleep(.1)

                # Evaluate the difference in the bobber over a 0.1 second period
                if os.path.exists("BobberLast.png"):
                    im1 = ImageChops.Image.open("BobberCurrent.png")
                    im2 = ImageChops.Image.open("BobberLast.png")
                    image_diff = rmsdiff(im1,im2)
                    # print(image_diff) # Uncomment to view splash values
                    # Threshold for splash detection (Found via the line above)
                    if image_diff > 25:
                        print("Splash detected")
                        time.sleep(.1)
                        autoit.control_send("World of Warcraft", "", "{F}", mode=0) # Interact Key (Catch Fish)
                        time.sleep(1)
                        autoit.control_send("World of Warcraft", "", "{1}", mode=0) # Cast Line
                        LastCast = time.time()
                        time.sleep(2) # Wait for previous bobber to disappear
                        break # Escape the While Loop that is watching the bobber
                    
                image.save("BobberLast.png")

            # After monitoring the bobber, remove the temp file
            try:
                os.remove("BobberLast.png")
            except Exception as e:
                print("No leftover bobber image")

    except Exception as e:
        print(e)