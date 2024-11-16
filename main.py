import tkinter as tk
from welcome_page import WelcomePage
from menu import MenuPage


def go_to_menu():
    """Transition to the menu page."""
    for widget in root.winfo_children():
        widget.destroy()  # Clear all widgets
    MenuPage(root)  # Initialize the menu page


# Initialize the root Tkinter window
root = tk.Tk()

# Start with the welcome page
WelcomePage(root, on_continue=go_to_menu)

# Run the application
root.mainloop()
