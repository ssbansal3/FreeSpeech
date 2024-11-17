import tkinter as tk
from welcome_page import WelcomePage
from menu import MenuPage


def go_to_menu():
    """Transition to the menu page."""
    for widget in root.winfo_children():
        widget.destroy()  # Clear all widgets
    MenuPage(root, on_back=go_to_welcome)  # Pass callback to return to the welcome page


def go_to_welcome():
    """Transition back to the welcome page."""
    for widget in root.winfo_children():
        widget.destroy()  # Clear all widgets
    WelcomePage(root, on_continue=go_to_menu)  # Reinitialize the welcome page


# Initialize the root Tkinter window
root = tk.Tk()

# Start with the welcome page
WelcomePage(root, on_continue=go_to_menu)

# Run the application
root.mainloop()
