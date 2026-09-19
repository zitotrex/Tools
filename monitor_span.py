import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

MOD_ALT = 0x0001
MOD_WIN = 0x0008
VK_UP = 0x26
WM_HOTKEY = 0x0312


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt_x", wintypes.LONG),
        ("pt_y", wintypes.LONG),
    ]


print("Registering Win+Alt+Up...")

result = user32.RegisterHotKey(
    None,
    1,
    MOD_WIN | MOD_ALT,
    VK_UP
)

print("RegisterHotKey result:", result)

if not result:
    print("Error:", ctypes.WinError(ctypes.get_last_error()))
    raise SystemExit

print("Registered successfully.")
print("Press Win+Alt+Up.")

msg = MSG()

while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
    if msg.message == WM_HOTKEY:
        print("HOTKEY RECEIVED!")

user32.UnregisterHotKey(None, 1)