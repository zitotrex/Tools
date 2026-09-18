import tkinter as tk
from tkinter import ttk
import ctypes
import time

# Windows API constants for key presses
VK_MENU = 0x12     # Alt key
VK_TAB = 0x09      # Tab key
VK_CONTROL = 0x11  # Ctrl key
VK_V = 0x56        # 'V' key
KEYEVENTF_KEYUP = 0x0002

user32 = ctypes.windll.user32

def send_key_down(vk_code):
    user32.keybd_event(vk_code, 0, 0, 0)

def send_key_up(vk_code):
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

def paste_to_firefox(text_to_paste):
    if not text_to_paste.strip():
        return

    # 1. Copy text to system clipboard
    root.clipboard_clear()
    root.clipboard_append(text_to_paste.strip())
    root.update()

    # 2. Simulate Alt + Tab to return to Firefox
    send_key_down(VK_MENU)
    send_key_down(VK_TAB)
    time.sleep(0.05)
    send_key_up(VK_TAB)
    send_key_up(VK_MENU)

    # 3. Brief pause for OS window focus transition
    time.sleep(0.12)

    # 4. Simulate Ctrl + V to paste
    send_key_down(VK_CONTROL)
    send_key_down(VK_V)
    time.sleep(0.05)
    send_key_up(VK_V)
    send_key_up(VK_CONTROL)

# --- GUI Setup ---
COMMON_ICONS = [
    "fa-solid fa-graduation-cap",
    "fa-solid fa-calculator",
    "fa-solid fa-user",
    "fa-solid fa-users",
    "fa-solid fa-check-square",
    "fa-solid fa-book",
    "fa-solid fa-envelope",
    "fa-solid fa-phone",
    "fa-solid fa-magnifying-glass",
    "fa-solid fa-calendar",
    "fa-solid fa-location-dot",
    "fa-solid fa-link",
]

root = tk.Tk()
root.title("FA Helper")
root.attributes('-topmost', True)
root.resizable(False, False)

frame = ttk.Frame(root, padding=8)
frame.pack(fill='both', expand=True)

ttk.Label(frame, text="Click to Paste:", font=('Segoe UI', 9, 'bold')).pack(anchor='w', pady=(0, 4))

for icon in COMMON_ICONS:
    btn = ttk.Button(
        frame, 
        text=icon, 
        command=lambda i=icon: paste_to_firefox(i)
    )
    btn.pack(fill='x', pady=1)

ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=6)

custom_frame = ttk.Frame(frame)
custom_frame.pack(fill='x')

entry = ttk.Entry(custom_frame)
entry.pack(side='left', fill='x', expand=True, padx=(0, 4))
entry.bind("<Return>", lambda event: paste_to_firefox(entry.get()))

send_btn = ttk.Button(
    custom_frame, 
    text="Paste Custom", 
    command=lambda: paste_to_firefox(entry.get())
)
send_btn.pack(side='right')

root.mainloop()