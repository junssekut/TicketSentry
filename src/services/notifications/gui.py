"""
GUI Popup Notification Strategy.
"""
import tkinter as tk
from tkinter import ttk
import webbrowser
import multiprocessing
import pyperclip
from src.services.notifications.base import NotificationStrategy
from src.services.sentry_service import SentryService

def _launch_gui_process(url: str):
    """
    Internal function to run the GUI in a separate process.
    """
    root = tk.Tk()
    root.title("SAT-Miner: Link Detected")
    
    # Window Configuration
    window_width = 500
    window_height = 220
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    root.resizable(False, False)
    
    # Always on Top & Focus
    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()
    
    # Styling
    bg_color = "#1e1e1e"
    accent_color = "#3b8ed0"
    
    root.configure(bg=bg_color)
    
    # Main Frame
    main_frame = tk.Frame(root, bg=bg_color, padx=20, pady=20)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Header
    tk.Label(
        main_frame, 
        text="🚨 Link Detected!", 
        font=("Segoe UI", 16, "bold"),
        bg=bg_color, 
        fg="#ff4444"
    ).pack(pady=(0, 10))
    
    # URL Display
    display_url = url if len(url) < 50 else url[:47] + "..."
    tk.Label(
        main_frame, 
        text=display_url, 
        font=("Consolas", 11),
        bg="#2d2d2d", 
        fg="#00ff00",
        padx=10,
        pady=5,
        relief="flat"
    ).pack(fill=tk.X, pady=10)
    
    # Buttons
    btn_frame = tk.Frame(main_frame, bg=bg_color)
    btn_frame.pack(pady=15)
    
    def copy_link():
        pyperclip.copy(url)
        btn_copy.config(text="Copied!", bg="#28a745")
        root.after(2000, lambda: btn_copy.config(text="Copy to Clipboard", bg=accent_color))

    def open_browser():
        webbrowser.open(url)
        root.destroy()

    def create_btn(parent, text, command, bg):
        return tk.Button(
            parent, text=text, command=command, bg=bg, fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", padx=15, pady=5, cursor="hand2"
        )

    btn_copy = create_btn(btn_frame, "Copy to Clipboard", copy_link, accent_color)
    btn_copy.pack(side=tk.LEFT, padx=5)
    
    create_btn(btn_frame, "Open Link", open_browser, "#555555").pack(side=tk.LEFT, padx=5)
    create_btn(btn_frame, "Dismiss", root.destroy, "#d9534f").pack(side=tk.LEFT, padx=5)

    root.mainloop()

class GuiNotification(NotificationStrategy):
    """
    Spawns a visual alert window on top of other applications.
    """
    def send(self, message: str, **kwargs):
        try:
            p = multiprocessing.Process(target=_launch_gui_process, args=(message,))
            p.start()
        except Exception as e:
            print(f"[!] Failed to launch GUI notification: {e}")
            SentryService.capture_exception(e)
            print(f"[!] Failed to launch GUI notification: {e}")
