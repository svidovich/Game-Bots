import tkinter as tk
import random
import time
import threading
import pyautogui
import keyboard
import autoit
import math
import mouse

# Smoothly moves the mouse from the current position to a target position (x2, y2).
# Incorporates random movement patterns to simulate human-like behavior.
def smoothMove(x2, y2):
    try:
        x1, y1 = mouse.get_position()
        trig = random.randint(1, 4)
        if (abs(x2 - x1) > 750) or (abs(y2 - y1) > 750):
            amplitude = random.randint(75, 100)
            duration = random.uniform(0.75, 1)
        elif (abs(x2 - x1) > 350) or (abs(y2 - y1) > 500):
            amplitude = random.randint(50, 75)
            duration = random.uniform(0.5, .75)
        elif (abs(x2 - x1) > 75) or (abs(y2 - y1) > 75):
            amplitude = random.randint(25, 50)
            duration = random.uniform(0.5, .75)
        else: # Very Short Movements Don't Arc Up/Down
            amplitude = 0
            trig = 5
            duration = random.uniform(0.25, .5)
        points = []
        num_points = int(duration * 75)
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
            elif trig == 5: # Very Short Movements don't Arc Up/Down
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
    except Exception as e:
        print("smoothMove() Error: " + str(e))

class AutoClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Auto Clicker")
        self.master.geometry("150x100+0+0")  # Set window size and position
        self.master.resizable(False, False)  # Make the window unresizable
        self.master.attributes('-topmost', True)  # Set the window to always be on top

        # Bind mouse events for dragging the window
        self.master.bind("<Button-1>", self.on_click)
        self.master.bind("<B1-Motion>", self.on_drag)

        # Input for minimum seconds
        tk.Label(master, text="Min Seconds:").grid(row=0, column=0)
        self.min_seconds = tk.Entry(master, width=10)
        self.min_seconds.grid(row=0, column=1)
        self.min_seconds.insert(0, ".5")  # Set default value for min_seconds

        # Input for maximum seconds
        tk.Label(master, text="Max Seconds:").grid(row=1, column=0)
        self.max_seconds = tk.Entry(master, width=10)
        self.max_seconds.grid(row=1, column=1)
        self.max_seconds.insert(0, ".75")  # Set default value for max_seconds

        # Start button
        self.start_button = tk.Button(master, text="Start (Insert)", command=self.start_clicking)
        self.start_button.grid(row=2, column=0, columnspan=2)

        # Stop button
        self.stop_button = tk.Button(master, text="Stop (Home)", command=self.stop_clicking)
        self.stop_button.grid(row=3, column=0, columnspan=2)

        self.clicking = False
        self.adjusting = False
        self.mouse_offset = 1  # +/- offset for mouse position (1 pixel)
        self.center_x = None
        self.center_y = None
        self.last_pause_time = time.time()  # Initialize the last pause time
        self.pause_interval = random.randint(160,190)

        # Bind global hotkeys
        keyboard.add_hotkey('insert', self.start_clicking)
        keyboard.add_hotkey('home', self.stop_clicking)

    def on_click(self, event):
        """ Start dragging the window. """
        self.dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag(self, event):
        """ Drag the window around based on mouse movement. """
        if self.dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            x = self.master.winfo_x() + dx
            y = self.master.winfo_y() + dy
            self.master.geometry(f"+{x}+{y}")

    def start_clicking(self):
        if not self.clicking:  # Start clicking only if it's not already
            # Activate RuneLite window
            autoit.win_activate("RuneLite")  # Use the exact title of the RuneLite window
            self.center_x, self.center_y = pyautogui.position()  # Set the center position
            self.clicking = True  # Set clicking flag
            self.adjusting = True  # Set adjusting flag
            self.last_pause_time = time.time()  # Reset the pause timer
            thread = threading.Thread(target=self.click)
            thread.start()  # Start the clicking thread
            threading.Thread(target=self.adjust_mouse_position_periodically, daemon=True).start()  # Start position adjustment

    def stop_clicking(self):
        self.clicking = False  # Stop clicking
        self.adjusting = False  # Set adjusting flag

    def click(self):
        """ Perform clicking action. """
        while self.clicking:
            try:
                min_sec = float(self.min_seconds.get())
                max_sec = float(self.max_seconds.get())

                if min_sec < 0 or max_sec < 0 or min_sec > max_sec:
                    continue  # Ignore invalid input

                # Click
                pyautogui.click()  # Left mouse click

                # Sleep for a random interval
                interval = random.uniform(min_sec, max_sec)
                time.sleep(interval)

                # Check if we need to pause clicking every 3 minutes
                if time.time() > self.last_pause_time + self.pause_interval:
                    self.stop_clicking()
                    smoothMove(random.randint(0,700),random.randint(0,1080))
                    try:
                        autoit.win_activate("Auto Clicker") # Bring VSCodium Client to the Foreground
                    except Exception as e:
                        print(e)
                    time.sleep(random.randint(20, 30))  # Pause for 20-30 seconds
                    try:
                        autoit.win_activate("RuneLite") # Bring Runescape Client to the Foreground
                    except Exception as e:
                        print(e)
                    smoothMove(self.center_x,self.center_y)
                    self.last_pause_time = time.time()  # Update last pause time
                    self.pause_interval = random.randint(160,190)
                    self.start_clicking()  # Restart clicking

            except ValueError:
                continue  # If input is not a float, skip

    def adjust_mouse_position_periodically(self):
        """ Adjust the mouse position slightly every 10 seconds. """
        while self.clicking:  # Run this thread as long as clicking is active
            self.adjust_mouse_position()
            time.sleep(random.uniform(8,12))  # Wait for 10 seconds

    def adjust_mouse_position(self):
        """ Adjust the mouse position slightly within ±1 pixel of the center. """
        if self.center_x is not None and self.center_y is not None:
            delta_x = random.randint(-self.mouse_offset, self.mouse_offset)
            delta_y = random.randint(-self.mouse_offset, self.mouse_offset)
            new_x = self.center_x + delta_x
            new_y = self.center_y + delta_y
            smoothMove(new_x, new_y)

if __name__ == "__main__":
    root = tk.Tk()
    auto_clicker = AutoClicker(root)
    root.mainloop()