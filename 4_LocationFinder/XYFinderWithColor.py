import tkinter as tk
import pyautogui
import keyboard
import pyperclip
from PIL import ImageGrab

class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Tracker")
        self.root.geometry("300x220+0+0")  # Width x Height + x_position + y_position
        self.root.configure(bg="#f0f0f0")
        self.root.attributes('-topmost', True)  # Set the window to always be on top

        # Create a frame with padding for margins
        self.frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        self.frame.pack(expand=True, fill=tk.BOTH)

        # Instructions Label
        self.instruction_label = tk.Label(
            self.frame,
            text="This application tracks your mouse position.\nPress SHIFT to copy coordinates.\nPress CAPS LOCK to save color.\nPress ESC to exit.",
            bg="#f0f0f0",
            font=("Helvetica", 10)
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

        # Color Box Display
        self.color_box = tk.Label(self.frame, text=" ", bg="#ffffff", width=15, height=2, relief='solid', borderwidth=1)
        self.color_box.pack(pady=5)

        # Color Display
        self.color_label = tk.Label(
            self.frame,
            text="Color: None",
            bg="#f0f0f0",
            font=("Helvetica", 12)
        )
        self.color_label.pack(pady=5)

        # Last Copied Coordinates Display
        self.last_coord_label = tk.Label(
            self.frame,
            text="Last Copied: None",
            bg="#f0f0f0",
            font=("Helvetica", 10)
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
            # Format the coordinates for displaying
            coord_str = f"{x},{y}"
            self.coord_label.config(text=f"Mouse Coordinates: ({coord_str})")

            # Get the color under the cursor
            decimal_color = self.get_color_at_cursor(x, y)
            self.color_label.config(text=f"Color: {decimal_color}")
            self.color_box.config(bg=self.rgb_to_hex(decimal_color))

            self.root.after(100, self.track_mouse)  # Update every 100 ms

    def get_color_at_cursor(self, x, y):
        # Take a screenshot of the pixel where the mouse is pointing
        screen = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
        # Get the RGB values from the screenshot
        r, g, b = screen.getpixel((0, 0))
        return (r, g, b)

    def rgb_to_decimal(self, rgb):
        """Convert RGB tuple to a single decimal value."""
        r, g, b = rgb
        return (r << 16) | (g << 8) | b

    def rgb_to_hex(self, rgb):
        """Convert RGB tuple to hex color string."""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)

    def on_key_event(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'shift':
                self.running = False  # Suspend updates
                x, y = pyautogui.position()
                coord_str = f"{x},{y}"  # Prepare coordinates for clipboard
                pyperclip.copy(coord_str)  # Copy coordinates to clipboard
                self.last_coord_label.config(text=f"Last Copied: ({coord_str})")
                self.root.after(1000, self.resume_tracking)  # Resume after 1 second
            elif event.name == 'caps lock':
                x, y = pyautogui.position()
                rgb_color = self.get_color_at_cursor(x, y)
                decimal_value = self.rgb_to_decimal(rgb_color)
                pyperclip.copy(str(decimal_value))  # Copy decimal color to clipboard
                print(f"Copied color in decimal format: {decimal_value}")  # Print for confirmation

    def resume_tracking(self):
        self.running = True  # Resume updates
        self.track_mouse()  # Start tracking again

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseTrackerApp(root)