import tkinter as tk
import random
import time
import threading
import pyautogui  # Make sure you have this installed for mouse clicks
import keyboard  # Ensure you have this installed

class AutoClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Auto Clicker")
        self.master.geometry("150x100+0+0")  # Set window size and position
        self.master.attributes('-topmost', True)  # Set the window to always be on top
        
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
        self.stop_button = tk.Button(master, text="Stop (Delete)", command=self.stop_clicking)
        self.stop_button.grid(row=3, column=0, columnspan=2)

        self.clicking = False
        
        # Bind global hotkeys
        keyboard.add_hotkey('insert', self.start_clicking)
        keyboard.add_hotkey('delete', self.stop_clicking)

    def start_clicking(self):
        if not self.clicking:  # Prevent starting if already clicking
            self.clicking = True
            thread = threading.Thread(target=self.click)
            thread.start()

    def stop_clicking(self):
        self.clicking = False

    def click(self):
        while self.clicking:
            try:
                min_sec = float(self.min_seconds.get())
                max_sec = float(self.max_seconds.get())
                if min_sec < 0 or max_sec < 0 or min_sec > max_sec:
                    continue  # Ignore invalid input
                interval = random.uniform(min_sec, max_sec)
                pyautogui.click()  # Left mouse click
                time.sleep(interval)  # Sleep for a random time
            except ValueError:
                continue  # If input is not a float, skip


if __name__ == "__main__":
    root = tk.Tk()
    auto_clicker = AutoClicker(root)
    root.mainloop()