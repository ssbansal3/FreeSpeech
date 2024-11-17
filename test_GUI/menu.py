import tkinter as tk
import queue

class MenuPage:
    """A class to create the menu page."""

    def __init__(self, root, on_back, event_queue):
        self.root = root
        self.on_back = on_back  # Callback function for returning to the welcome page
        self.event_queue = event_queue  # Event queue for EEG inputs
        self.current_side = "left"  # Tracks the active side for navigation
        self.alphabet = [chr(i) for i in range(65, 91)] + ["space"]
        self.special_characters = [".", ",", "!", "?", "@", "#", "$", "%", "&", "*"]
        self.message = ""  # Stores the constructed message
        self.is_done = False  # Tracks if the user has completed their message
        self.create_ui()
        self.poll_events()  # Start polling the event queue

    def create_ui(self):
        self.root.title("FreeSpeech - Menu")
        self.root.geometry("1100x900")
        self.root.configure(bg="#2b2b2b")

        # Title Label
        label = tk.Label(
            self.root,
            text="Communicator",
            font=("Helvetica", 30, "bold"),
            fg="#FF377F",
            bg="#2b2b2b",
        )
        label.pack(pady=10)

        # Instruction Prompt
        self.prompt = tk.Label(
            self.root,
            text="Navigate using Left/Right signals and blink to confirm selection.",
            font=("Helvetica", 14),
            fg="white",
            bg="#2b2b2b",
        )
        self.prompt.pack()

        # Container Frame for Panels
        self.panel_frame = tk.Frame(self.root, bg="#2b2b2b")
        self.panel_frame.pack(expand=True, fill="both")

        # Configure grid weights to center items
        self.panel_frame.columnconfigure((0, 1, 2), weight=1)
        self.panel_frame.rowconfigure(0, weight=1)

        # Left Panel (Alphabet)
        self.left_panel = tk.Label(
            self.panel_frame,
            text="\n".join(self.alphabet),
            font=("Helvetica", 16),
            justify="center",
            fg="white",
            bg="#444444",
            width=20,
        )
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Right Panel (Special Characters)
        self.right_panel = tk.Label(
            self.panel_frame,
            text="\n".join(self.special_characters),
            font=("Helvetica", 16),
            justify="center",
            fg="white",
            bg="#2b2b2b",
            width=20,
        )
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        # "Done" Panel
        self.done_panel = tk.Label(
            self.panel_frame,
            text="Done",
            font=("Helvetica", 18, "bold"),
            justify="center",
            fg="white",
            bg="#2b2b2b",
            width=20,
        )
        self.done_panel.grid(row=0, column=2, padx=10, pady=10, sticky="n")

        # Message Box
        self.message_box = tk.Text(
            self.root,
            font=("Helvetica", 14),
            height=8,  # Reduced height
            width=50,  # Adjusted width
            bg="#1f1f1f",
            fg="white",
            state="disabled",
            wrap="word",  # Wraps text within the box
        )
        self.message_box.pack(pady=10)

    # Remove key bindings as we will use EEG inputs
    # Event handling methods
    def navigate_left(self):
        if self.current_side == "right":
            self.current_side = "left"
        elif self.current_side == "done":
            self.current_side = "right"
        self.update_hover_effect()

    def navigate_right(self):
        if self.current_side == "left":
            self.current_side = "right"
        elif self.current_side == "right":
            self.current_side = "done"
        self.update_hover_effect()

    def update_hover_effect(self):
        if self.current_side == "left":
            self.left_panel.config(bg="#FF377F")
            self.right_panel.config(bg="#2b2b2b")
            self.done_panel.config(bg="#2b2b2b")
        elif self.current_side == "right":
            self.left_panel.config(bg="#2b2b2b")
            self.right_panel.config(bg="#FF377F")
            self.done_panel.config(bg="#2b2b2b")
        elif self.current_side == "done":
            self.left_panel.config(bg="#2b2b2b")
            self.right_panel.config(bg="#2b2b2b")
            self.done_panel.config(bg="#FF377F")

    def select_group(self):
        if self.current_side == "left":
            self.start_selection(self.alphabet)
        elif self.current_side == "right":
            self.start_selection(self.special_characters)
        elif self.current_side == "done":
            self.show_final_message()

    def start_selection(self, items):
        if len(items) == 1:
            self.finalize_character(items[0])
            return

        self.selection_loop(items)

    def selection_loop(self, items):
        if len(items) == 2:
            self.show_final_selection(items)
            return

        mid = len(items) // 2
        left = items[:mid]
        right = items[mid:]

        self.update_panels(left, right)
        self.current_side = "left"  # Reset to left for new selection
        self.update_hover_effect()

    def update_panels(self, left_items, right_items):
        self.alphabet = left_items
        self.special_characters = right_items

        self.left_panel.config(text="\n".join(left_items))
        self.right_panel.config(text="\n".join(right_items))

    def show_final_selection(self, items):
        self.update_panels([items[0]], [items[1]])
        self.current_side = "left"  # Reset to left for final selection
        self.update_hover_effect()
        self.awaiting_final_selection = True
        self.final_items = items

    def get_selection(self, items):
        return items[0] if self.current_side == "left" else items[1]

    def finalize_character(self, selected):
        self.message += " " if selected == "space" else selected
        self.update_message_box()
        self.reset_panels()

    def update_message_box(self):
        self.message_box.config(state="normal")
        self.message_box.delete(1.0, tk.END)
        self.message_box.insert(tk.END, self.message)
        self.message_box.config(state="disabled")

    def reset_panels(self):
        self.alphabet = [chr(i) for i in range(65, 91)] + ["space"]
        self.special_characters = [".", ",", "!", "?", "@", "#", "$", "%", "&", "*"]
        self.update_panels(self.alphabet, self.special_characters)
        self.current_side = "left"
        self.update_hover_effect()
        self.awaiting_final_selection = False
        self.final_items = None

    def show_final_message(self):
        self.is_done = True
        self.panel_frame.pack_forget()
        self.prompt.config(
            text="Your message is ready! Blink to complete run.",
        )
        self.message_box.config(state="normal")
        # Stop polling events
        self.polling = False
        # Optionally, you can save the message or perform other actions

    # Polling method to check the event queue
    def poll_events(self):
        try:
            while True:
                event = self.event_queue.get_nowait()
                if event == "left":
                    self.navigate_left()
                elif event == "right":
                    self.navigate_right()
                elif event == "blink":
                    if self.is_done:
                        # Close the application or perform any cleanup
                        self.root.quit()
                    elif hasattr(self, 'awaiting_final_selection') and self.awaiting_final_selection:
                        selected = self.get_selection(self.final_items)
                        self.finalize_character(selected)
                    else:
                        self.select_group()
                elif event == "escape":
                    self.on_back()
        except queue.Empty:
            pass
        # Schedule the next poll
        if not self.is_done:
            self.root.after(100, self.poll_events)  # Poll every 100 ms
