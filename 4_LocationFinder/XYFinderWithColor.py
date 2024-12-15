import tkinter as tk
import pyautogui
import keyboard
import pyperclip
from PIL import ImageGrab

class MouseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Tracker")
        self.root.geometry("300x250+0+0")  # Increased height for additional elements
        self.root.configure(bg="#f0f0f0")
        self.root.attributes('-topmost', True)  # Set the window to always be on top
        
        # Create a frame with padding for margins
        self.frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        self.frame.pack(expand=True, fill=tk.BOTH)
        
        # Instructions Label
        self.instruction_label = tk.Label(
            self.frame,
            text="This application tracks your mouse position.\nPress SHIFT to copy coordinates.\nPress CAPS LOCK to save color.",
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

        # Color Display
        self.color_label = tk.Label(
            self.frame,
            text="Color: None",
            bg="#f0f0f0",
            font=("Helvetica", 12)
        )
        self.color_label.pack(pady=5)

        # Create a frame for the color box and dropdown
        self.color_frame = tk.Frame(self.frame, bg="#f0f0f0")
        self.color_frame.pack(pady=5)  # Add padding for spacing

        # Color Box Display
        self.color_box = tk.Label(self.color_frame, text=" ", bg="#ffffff", width=15, height=2, relief='solid', borderwidth=1)
        self.color_box.pack(side=tk.LEFT)

        # Color Format Dropdown
        self.color_format = tk.StringVar(self.frame)
        self.color_format.set("Decimal")  # Set default value to Decimal
        self.format_menu = tk.OptionMenu(self.color_frame, self.color_format, "HEX", "RGB", "Decimal")
        self.format_menu.pack(side=tk.LEFT, padx=5)  # Place the dropdown next to the color box

        # Last Copied Coordinates Display
        self.last_coord_frame = tk.Frame(self.frame, bg="#f0f0f0")
        self.last_coord_frame.pack(pady=(5, 2))  # Padding for spacing
        tk.Label(self.last_coord_frame, text="Last Copied: ", bg="#f0f0f0").pack(side=tk.LEFT)  # Static text
        self.last_coord_text = tk.Text(self.last_coord_frame, height=1, width=25, wrap='none', bg="#ffffff")
        self.last_coord_text.insert(tk.END, "None")
        self.last_coord_text.bind("<Button-1>", self.copy_last_coord)
        self.last_coord_text.pack(side=tk.LEFT)

        # Last Copied Color Display
        self.last_color_frame = tk.Frame(self.frame, bg="#f0f0f0")
        self.last_color_frame.pack(pady=(2, 5))  # Padding for spacing
        tk.Label(self.last_color_frame, text="Last Copied Color: ", bg="#f0f0f0").pack(side=tk.LEFT)  # Static text
        self.last_color_text = tk.Text(self.last_color_frame, height=1, width=25, wrap='none', bg="#ffffff")
        self.last_color_text.insert(tk.END, "None")
        self.last_color_text.bind("<Button-1>", self.copy_last_color)
        self.last_color_text.pack(side=tk.LEFT)

        # Start tracking mouse position
        self.running = True
        self.track_mouse()

        # Set up keyboard hooks
        keyboard.hook(self.on_key_event)
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
            # Determine the color format to display
            if self.color_format.get() == "HEX":
                color_output = self.rgb_to_hex(decimal_color)
                color_display = f"Color: {color_output}"
            elif self.color_format.get() == "RGB":
                color_display = f"Color: {decimal_color}"
            elif self.color_format.get() == "Decimal":
                color_display = f"Color: {self.rgb_to_decimal(decimal_color)}"
            else:
                color_display = "Color: None"
            self.color_label.config(text=color_display)
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

    def copy_last_coord(self, event):
        """Copy the last copied coordinates text to the clipboard."""
        text = self.last_coord_text.get("1.0", tk.END).strip()
        pyperclip.copy(text)

    def copy_last_color(self, event):
        """Copy the last copied color text to the clipboard."""
        text = self.last_color_text.get("1.0", tk.END).strip()
        pyperclip.copy(text)

    def on_key_event(self, event):
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'shift':
                self.running = False  # Suspend updates
                x, y = pyautogui.position()
                coord_str = f"{x},{y}"  # Prepare coordinates for clipboard
                pyperclip.copy(coord_str)  # Copy coordinates to clipboard
                self.last_coord_text.delete("1.0", tk.END)  # Clear existing text
                self.last_coord_text.insert(tk.END, coord_str)  # Update with new coordinates
                self.root.after(1000, self.resume_tracking)  # Resume after 1 second
            elif event.name == 'caps lock':
                x, y = pyautogui.position()
                rgb_color = self.get_color_at_cursor(x, y)

                # Copy selected color format to clipboard
                if self.color_format.get() == "HEX":
                    color_value = self.rgb_to_hex(rgb_color)
                elif self.color_format.get() == "RGB":
                    color_value = rgb_color
                elif self.color_format.get() == "Decimal":
                    color_value = self.rgb_to_decimal(rgb_color)
                else:
                    color_value = "None"  # No valid format selected

                pyperclip.copy(str(color_value))  # Copy the selected color format to clipboard
                self.last_color_text.delete("1.0", tk.END)  # Clear existing text
                self.last_color_text.insert(tk.END, str(color_value))  # Update with new color
                print(f"Copied color in {self.color_format.get().lower()} format: {color_value}")  # Print for confirmation

    def resume_tracking(self):
        self.running = True  # Resume updates
        self.track_mouse()  # Start tracking again

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseTrackerApp(root)