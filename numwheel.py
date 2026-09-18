import ctypes
import time

# Windows API Constants
WM_MOUSEWHEEL = 0x020A
WHEEL_DELTA = 120

# Virtual Key Codes
VK_SCROLL = 0x14   # Scroll Lock key
VK_NUMPAD8 = 0x68  # Numpad 8
VK_NUMPAD2 = 0x62  # Numpad 2

user32 = ctypes.windll.user32

def is_scroll_lock_on():
    """Checks if Scroll Lock is toggled on."""
    # GetKeyState returns a 1 in the lowest bit if the key is toggled on
    return (user32.GetKeyState(VK_SCROLL) & 1) == 1

def is_key_pressed(vk_code):
    """Checks if a specific key is currently being held down."""
    return (user32.GetAsyncKeyState(vk_code) & 0x8000) != 0

def send_scroll(direction):
    """Sends a native hardware mouse wheel signal to the active window."""
    w_param = (WHEEL_DELTA << 16) if direction == "up" else ((-WHEEL_DELTA) << 16) & 0xFFFFFFFF
    active_window = user32.GetForegroundWindow()
    user32.PostMessageW(active_window, WM_MOUSEWHEEL, w_param, 0)

print("Numpad Scroll Emulator active.")
print("-> Turn ON Scroll Lock to use Numpad 8/2 for scrolling.")
print("-> Turn OFF Scroll Lock to use Numpad normally.")

try:
    while True:
        # Only intercept keys if Scroll Lock indicator light is ON
        if is_scroll_lock_on():
            if is_key_pressed(VK_NUMPAD8):
                send_scroll("up")
                time.sleep(0.08)  # Smooth scroll delay
                
            elif is_key_pressed(VK_NUMPAD2):
                send_scroll("down")
                time.sleep(0.08)  # Smooth scroll delay
                
        time.sleep(0.01)  # Keeps CPU usage at 0%
except KeyboardInterrupt:
    print("\nScript stopped.")
