import tkinter as tk


class MenuPage:
    """A class to create the menu page."""
    def __init__(self, root):
        self.root = root
        self.create_ui()

    def create_ui(self):
        self.root.title("FreeSpeech - Menu")
        self.root.geometry("1100x700")  # Set the dimensions of the screen
        self.root.configure(bg="#2b2b2b")  # Set the background color of the screen

        # Add a label to indicate the menu
        label = tk.Label(
            self.root,
            text="Menu Page",
            font=("Helvetica", 30, "bold"),
            fg="#FF377F",
            bg="#2b2b2b"
        )
        label.pack(expand=True)
