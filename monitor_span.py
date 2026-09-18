import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

MOD_ALT = 0x0001
MOD_WIN = 0x0008

VK_LEFT = 0x25
VK_UP = 0x26
VK_RIGHT = 0x27
VK_DOWN = 0x28
VK_0 = 0x30

WM_HOTKEY = 0x0312

SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
    ]


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


def get_monitors():
    monitors = []

    MonitorEnumProc = ctypes.WINFUNCTYPE(
        ctypes.c_int,
        wintypes.HMONITOR,
        wintypes.HDC,
        ctypes.POINTER(RECT),
        wintypes.LPARAM,
    )

    def callback(hmonitor, hdc, rect, lparam):
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        user32.GetMonitorInfoW(hmonitor, ctypes.byref(info))

        r = info.rcMonitor
        monitors.append({
            "left": r.left,
            "top": r.top,
            "right": r.right,
            "bottom": r.bottom,
        })
        return 1

    user32.EnumDisplayMonitors(None, None, MonitorEnumProc(callback), 0)
    return monitors


def get_window_rect(hwnd):
    rect = RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None
    return rect


def get_current_monitor(hwnd, monitors):
    rect = get_window_rect(hwnd)
    if not rect:
        return None

    cx = (rect.left + rect.right) / 2
    cy = (rect.top + rect.bottom) / 2

    containing = [
        m for m in monitors
        if m["left"] <= cx < m["right"]
        and m["top"] <= cy < m["bottom"]
    ]

    if containing:
        return min(
            containing,
            key=lambda m: (
                (m["right"] - m["left"]) * (m["bottom"] - m["top"])
            )
        )

    # Fallback for a window straddling monitors.
    return min(
        monitors,
        key=lambda m: (
            abs(((m["left"] + m["right"]) / 2) - cx)
            + abs(((m["top"] + m["bottom"]) / 2) - cy)
        )
    )


def overlap(a1, a2, b1, b2):
    return max(0, min(a2, b2) - max(a1, b1))


def find_adjacent(current, monitors, direction):
    candidates = []

    for m in monitors:
        if m is current:
            continue

        if direction == "up":
            gap = current["top"] - m["bottom"]
            shared = overlap(
                current["left"], current["right"],
                m["left"], m["right"]
            )
        elif direction == "down":
            gap = m["top"] - current["bottom"]
            shared = overlap(
                current["left"], current["right"],
                m["left"], m["right"]
            )
        elif direction == "left":
            gap = current["left"] - m["right"]
            shared = overlap(
                current["top"], current["bottom"],
                m["top"], m["bottom"]
            )
        else:  # right
            gap = m["left"] - current["right"]
            shared = overlap(
                current["top"], current["bottom"],
                m["top"], m["bottom"]
            )

        if gap >= 0 and shared > 0:
            candidates.append((gap, -shared, m))

    if candidates:
        candidates.sort(key=lambda x: (x[0], x[1]))
        return candidates[0][2]

    # If there is no directly touching monitor, find the nearest one
    # in the requested direction.
    directional = []

    for m in monitors:
        if direction == "up":
            distance = current["top"] - m["bottom"]
            center_distance = abs(
                ((current["left"] + current["right"]) / 2)
                - ((m["left"] + m["right"]) / 2)
            )
        elif direction == "down":
            distance = m["top"] - current["bottom"]
            center_distance = abs(
                ((current["left"] + current["right"]) / 2)
                - ((m["left"] + m["right"]) / 2)
            )
        elif direction == "left":
            distance = current["left"] - m["right"]
            center_distance = abs(
                ((current["top"] + current["bottom"]) / 2)
                - ((m["top"] + m["bottom"]) / 2)
            )
        else:
            distance = m["left"] - current["right"]
            center_distance = abs(
                ((current["top"] + current["bottom"]) / 2)
                - ((m["top"] + m["bottom"]) / 2)
            )

        if distance >= 0:
            directional.append((distance, center_distance, m))

    if not directional:
        return None

    directional.sort(key=lambda x: (x[0], x[1]))
    return directional[0][2]


def set_window_rect(hwnd, left, top, right, bottom):
    user32.SetWindowPos(
        hwnd,
        None,
        left,
        top,
        right - left,
        bottom - top,
        SWP_NOZORDER | SWP_NOACTIVATE | SWP_SHOWWINDOW,
    )


def save_original(hwnd):
    rect = get_window_rect(hwnd)
    if rect:
        return (
            rect.left,
            rect.top,
            rect.right,
            rect.bottom,
        )
    return None


def restore_window(hwnd, rect):
    if rect:
        set_window_rect(hwnd, *rect)


def span(hwnd, direction):
    monitors = get_monitors()
    current = get_current_monitor(hwnd, monitors)

    if not current:
        return

    adjacent = find_adjacent(current, monitors, direction)

    if not adjacent:
        return

    if direction == "up":
        set_window_rect(
            hwnd,
            current["left"],
            adjacent["top"],
            current["right"],
            current["bottom"],
        )

    elif direction == "down":
        set_window_rect(
            hwnd,
            current["left"],
            current["top"],
            current["right"],
            adjacent["bottom"],
        )

    elif direction == "left":
        set_window_rect(
            hwnd,
            adjacent["left"],
            current["top"],
            current["right"],
            current["bottom"],
        )

    elif direction == "right":
        set_window_rect(
            hwnd,
            current["left"],
            current["top"],
            adjacent["right"],
            current["bottom"],
        )


# Hotkey IDs
HOTKEY_UP = 1
HOTKEY_RIGHT = 2
HOTKEY_DOWN = 3
HOTKEY_LEFT = 4
HOTKEY_RESTORE = 5

hotkeys = [
    (HOTKEY_UP, VK_UP),
    (HOTKEY_RIGHT, VK_RIGHT),
    (HOTKEY_DOWN, VK_DOWN),
    (HOTKEY_LEFT, VK_LEFT),
    (HOTKEY_RESTORE, VK_0),
]

for hotkey_id, key in hotkeys:
    if not user32.RegisterHotKey(
        None,
        hotkey_id,
        MOD_WIN | MOD_ALT,
        key,
    ):
        raise RuntimeError(
            f"Could not register Win+Alt hotkey (ID {hotkey_id}). "
            "It may already be in use."
        )

print("Monitor spanning active.")
print()
print("Win+Alt+Up     = span upward")
print("Win+Alt+Right  = span right")
print("Win+Alt+Down   = span downward")
print("Win+Alt+Left   = span left")
print("Win+Alt+0      = restore")
print()
print("Ctrl+C to exit.")

previous_rect = None
previous_hwnd = None

msg = MSG()

try:
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        if msg.message != WM_HOTKEY:
            continue

        hwnd = user32.GetForegroundWindow()

        if not hwnd:
            continue

        hotkey_id = msg.wParam

        if hotkey_id == HOTKEY_RESTORE:
            if hwnd == previous_hwnd:
                restore_window(hwnd, previous_rect)
            continue

        # Save the window's original position only when starting
        # a new spanning operation.
        if hwnd != previous_hwnd:
            previous_rect = save_original(hwnd)
            previous_hwnd = hwnd

        if hotkey_id == HOTKEY_UP:
            span(hwnd, "up")
        elif hotkey_id == HOTKEY_RIGHT:
            span(hwnd, "right")
        elif hotkey_id == HOTKEY_DOWN:
            span(hwnd, "down")
        elif hotkey_id == HOTKEY_LEFT:
            span(hwnd, "left")

finally:
    for hotkey_id, _ in hotkeys:
        user32.UnregisterHotKey(None, hotkey_id)
