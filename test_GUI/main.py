import tkinter as tk
from welcome_page import WelcomePage
from menu import MenuPage
import threading
import queue
from eeg_processing import EEGThread  # Import the EEG thread class

def go_to_menu():
    """Transition to the menu page."""
    for widget in root.winfo_children():
        widget.destroy()  # Clear all widgets
    # Pass the event queue to the MenuPage
    MenuPage(root, on_back=go_to_welcome, event_queue=event_queue)

def go_to_welcome():
    """Transition back to the welcome page."""
    for widget in root.winfo_children():
        widget.destroy()  # Clear all widgets
    # Pass the event queue to the WelcomePage
    WelcomePage(root, on_continue=go_to_menu, event_queue=event_queue)

# Initialize the root Tkinter window
root = tk.Tk()

# Create an event queue for communication between threads
event_queue = queue.Queue()

# Initialize and start the EEG thread
eeg_thread = EEGThread(event_queue)
eeg_thread.start()

# Start with the welcome page, passing the event queue
WelcomePage(root, on_continue=go_to_menu, event_queue=event_queue)

# Run the application
root.mainloop()

# Stop the EEG thread when the GUI is closed
eeg_thread.stop()
