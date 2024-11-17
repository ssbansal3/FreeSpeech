import tkinter as tk
import queue  # Added import statement for the queue module

class RoundedPanel(tk.Canvas):
    """A class to create a rounded rectangle panel."""
    def __init__(self, parent, width, height, radius, bg_color, **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent['bg'], highlightthickness=0, **kwargs)
        self.bg_color = bg_color
        self.radius = radius
        self.width = width
        self.height = height
        self.draw_rounded_panel()

    def draw_rounded_panel(self):
        """Draw a rounded rectangle panel."""
        radius = self.radius
        x1, y1 = 0, 0
        x2, y2 = self.width, self.height

        # Draw arcs for corners
        self.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, fill=self.bg_color, outline="")
        self.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, fill=self.bg_color, outline="")
        self.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, fill=self.bg_color, outline="")
        self.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, fill=self.bg_color, outline="")

        # Draw rectangles for the sides and center
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=self.bg_color, outline="")
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, fill=self.bg_color, outline="")

class WelcomePage:
    """A class to create the welcome page."""
    def __init__(self, root, on_continue, event_queue):
        self.root = root
        self.on_continue = on_continue
        self.event_queue = event_queue  # Event queue for EEG inputs
        self.create_ui()
        self.poll_events()  # Start polling the event queue

    def create_ui(self):
        self.root.title("FreeSpeech - Welcome")
        self.root.geometry("1100x700")  # Set the dimensions of the screen
        self.root.configure(bg="#2b2b2b")  # Set the background color of the screen

        # Create the rounded panel
        panel_width = 800
        panel_height = 625
        panel_radius = 30
        panel = RoundedPanel(self.root, width=panel_width, height=panel_height, radius=panel_radius, bg_color="#000000")
        panel.place(relx=0.5, rely=0.5, anchor="center")  # Center the panel on the screen

        # Add welcome message to the panel
        welcome_message = tk.Label(
            panel,
            text="\U0001F44B Welcome to FreeSpeech!",  # Wave emoji
            font=("Helvetica", 30, "bold"),
            fg="#FF377F",  # Message color
            bg="#000000"  # Panel background color
        )
        welcome_message.place(relx=0.5, rely=0.3, anchor="center")

        # Add sub-message to the panel
        sub_message = tk.Label(
            panel,
            text="Talk without talking",
            font=("Helvetica", 24, "italic"),
            fg="#FF377F",
            bg="#000000"
        )
        sub_message.place(relx=0.5, rely=0.5, anchor="center")

        # Add the instruction label to the panel
        instruction_label = tk.Label(
            panel,
            text="Blink to Continue",
            font=("Helvetica", 20, "italic"),
            fg="#FF377F",
            bg="#000000"
        )
        instruction_label.place(relx=0.5, rely=0.8, anchor="center")

    # Remove key binding method
    # Polling method to check the event queue
    def poll_events(self):
        try:
            while True:
                event = self.event_queue.get_nowait()
                if event == "blink":
                    self.on_continue()
                elif event == "escape":
                    self.root.quit()
        except queue.Empty:
            pass
        # Schedule the next poll
        self.root.after(100, self.poll_events)  # Poll every 100 ms

if __name__ == "__main__":
    import queue

    def go_to_menu():
        print("Proceeding to Menu Page")  # Placeholder for navigation to MenuPage

    root = tk.Tk()
    event_queue = queue.Queue()  # Create an event queue
    app = WelcomePage(root, on_continue=go_to_menu, event_queue=event_queue)
    root.mainloop()
