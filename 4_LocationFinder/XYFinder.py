import tkinter as tk
import pyautogui
import keyboard
import pyperclip

class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Tracker")
        self.root.geometry("300x150+0+0")  # Width x Height + x_position + y_position
        self.root.configure(bg="#f0f0f0")

        self.root.attributes('-topmost', True) # Set the window to always be on top

        # Create a frame with padding for margins
        self.frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        self.frame.pack(expand=True, fill=tk.BOTH)

        # Instructions Label
        self.instruction_label = tk.Label(
            self.frame,
            text="This application tracks your mouse position.\nPress SHIFT to copy coordinates.\nPress ESC to exit.",
            bg="#f0f0f0",
            font=("Helvetica", 10)  # Slightly reduced font size for better fit
        )
        self.instruction_label.pack(pady=5)

        # Coordinate Display
        self.coord_label = tk.Label(
            self.frame,
            text="Mouse Coordinates: (X: 0, Y: 0)",
            bg="#f0f0f0",
            font=("Helvetica", 12)
        )
        self.coord_label.pack(pady=5)

        # Last Copied Coordinates Display
        self.last_coord_label = tk.Label(
            self.frame,
            text="Last Copied: None",
            bg="#f0f0f0",
            font=("Helvetica", 10)  # Maintained reduced font size
        )
        self.last_coord_label.pack(pady=5)

        # Start tracking mouse position
        self.running = True
        self.track_mouse()

        # Set up keyboard hooks
        keyboard.hook(self.on_key_event)
        # Add ESC key press to close the application
        keyboard.add_hotkey('esc', self.root.quit)

        # Run the GUI main loop
        self.root.mainloop()

    def track_mouse(self):
        if self.running:
            x, y = pyautogui.position()
            # Format the coordinates for copying
            coord_str = f"{x},{y}"
            self.coord_label.config(text=f"Mouse Coordinates: ({coord_str})")
            self.root.after(100, self.track_mouse)  # Update every 100 ms

    def on_key_event(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'shift':
                self.running = False  # Suspend updates
                x, y = pyautogui.position()
                coord_str = f"{x},{y}"  # Prepare coordinates for clipboard
                pyperclip.copy(coord_str)  # Copy coordinates to clipboard
                self.last_coord_label.config(text=f"Last Copied: ({coord_str})")
                self.root.after(1000, self.resume_tracking)  # Resume after 1 second

    def resume_tracking(self):
        self.running = True  # Resume updates
        self.track_mouse()  # Start tracking again

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseTrackerApp(root)