# -*- coding: utf-8 -*-
"""
CoordClicker
A small clicker tool with hotkeys. Run it with: python coord_clicker.py

What it does
- Hover your mouse over the spot you want to click and press a hotkey to
  save that position. The window under your mouse becomes the target.
- Clicks are sent straight to the target window, so your real mouse is
  not used and you can keep using your computer normally.
- There are two saved points, "Right" and "Left". Each one can be set to
  Left click, Right click, Scroll Down or Scroll Up.
- The loop: do the Right action N times (the "Amount"), do the Left
  action once, then repeat until you stop it.
- Three hotkeys: set Right point, set Left point, Start/Stop.
  You can use combos like "ctrl+shift+r" or a single key like "f1".
- All settings are saved and loaded the next time you open it.

Requirements
- Windows only.
- pip install keyboard   (needed for the hotkeys)
- Everything else is built into Python.
"""

import ctypes
import ctypes.wintypes as wintypes
import json
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import keyboard as kb
    KEYBOARD_OK = True
except ImportError:
    KEYBOARD_OK = False

try:
    user32 = ctypes.windll.user32
    WINAPI_OK = True
except (AttributeError, OSError):
    user32 = None
    WINAPI_OK = False

# Save settings next to the exe (when built) or next to the script.
if getattr(sys, "frozen", False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(_BASE_DIR, "coord_clicker_settings.json")

# Colors used by the interface
C = {
    "bg":      "#12161c",
    "bg2":     "#0d1015",
    "panel":   "#181e26",
    "panel2":  "#1f2733",
    "border":  "#2a3341",
    "text":    "#e7ecf3",
    "muted":   "#7c8798",
    "accent":  "#4fa8ff",
    "accent2": "#8a6bff",
    "green":   "#4bd08a",
    "red":     "#ff5c6c",
    "gold":    "#ffb454",
}
FONT_HEAD  = ("Segoe UI", 13, "bold")
FONT_BODY  = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_MONO  = ("Consolas", 10)

# Window icon (small PNG stored right in the script so no extra files are needed)
ICON_PNG_B64 = (
    "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"
)


# Window helpers
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


def get_cursor_pos():
    """Where the mouse is on screen."""
    if not WINAPI_OK:
        return (0, 0)
    pt = POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)


def set_cursor_pos(x, y):
    if not WINAPI_OK:
        return
    user32.SetCursorPos(int(x), int(y))


def screen_to_client(hwnd, x, y):
    """Screen position -> position inside the window."""
    if not WINAPI_OK or not hwnd:
        return (x, y)
    pt = POINT(x, y)
    user32.ScreenToClient(hwnd, ctypes.byref(pt))
    return (pt.x, pt.y)


def client_to_screen(hwnd, x, y):
    """Position inside the window -> screen position."""
    if not WINAPI_OK or not hwnd:
        return (x, y)
    pt = POINT(x, y)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return (pt.x, pt.y)


def window_title(hwnd):
    if not WINAPI_OK or not hwnd:
        return ""
    length = user32.GetWindowTextLengthW(hwnd) + 1
    buf = ctypes.create_unicode_buffer(length)
    user32.GetWindowTextW(hwnd, buf, length)
    return buf.value.strip()


def is_window_valid(hwnd):
    return bool(WINAPI_OK and hwnd and user32.IsWindow(hwnd))


def scan_windows():
    """List all visible windows that have a title."""
    results = []
    if not WINAPI_OK:
        return results
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)

    def _cb(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            title = window_title(hwnd)
            if title:
                results.append((hwnd, title))
        return True

    user32.EnumWindows(WNDENUMPROC(_cb), 0)
    return results


# Sending clicks and scrolls to a window
WM_MOUSEMOVE   = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP   = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP   = 0x0205
WM_MOUSEWHEEL  = 0x020A
MK_LBUTTON     = 0x0001
MK_RBUTTON     = 0x0002
WHEEL_DELTA    = 120
GA_ROOT        = 2


def _make_lparam(x, y):
    """Packs x and y into one number, the way Windows expects."""
    return (int(y) & 0xFFFF) << 16 | (int(x) & 0xFFFF)


def _make_wheel_wparam(delta, keystate=0):
    """Packs the scroll amount the way Windows expects."""
    return ((int(delta) & 0xFFFF) << 16) | (int(keystate) & 0xFFFF)


def window_from_point(x, y):
    """Find the window under a screen position (used to auto-pick the target)."""
    if not WINAPI_OK:
        return None
    try:
        pt = POINT(x, y)
        hwnd = user32.WindowFromPoint(pt)
        if not hwnd:
            return None
        root = user32.GetAncestor(hwnd, GA_ROOT)
        return root or hwnd
    except Exception:
        return None


def _cursor_is_over_window(hwnd):
    """True if your real mouse is currently over the target window."""
    if not WINAPI_OK or not hwnd:
        return False
    try:
        pt = POINT(0, 0)
        if not user32.GetCursorPos(ctypes.byref(pt)):
            return False
        rect = wintypes.RECT()
        if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
            return False
        origin = POINT(0, 0)
        if not user32.ClientToScreen(hwnd, ctypes.byref(origin)):
            return False
        left, top = origin.x, origin.y
        right, bottom = left + rect.right, top + rect.bottom
        return left <= pt.x < right and top <= pt.y < bottom
    except Exception:
        return False


def send_click_bg(hwnd, x, y, button="left", hold=0.02):
    """Click at (x, y) inside the target window without using your mouse.

    Some games only listen to the real mouse position. If your mouse is
    sitting over the game window, this briefly moves it to the click spot
    and puts it straight back. Otherwise your mouse is not touched.
    Returns True if the click was sent."""
    if not WINAPI_OK or not hwnd:
        return False

    lparam = _make_lparam(x, y)
    down, up, mk = (
        (WM_RBUTTONDOWN, WM_RBUTTONUP, MK_RBUTTON) if button == "right"
        else (WM_LBUTTONDOWN, WM_LBUTTONUP, MK_LBUTTON))

    if _cursor_is_over_window(hwnd):
        try:
            orig = POINT(0, 0)
            user32.GetCursorPos(ctypes.byref(orig))
            origin = POINT(0, 0)
            if not user32.ClientToScreen(hwnd, ctypes.byref(origin)):
                return False
            user32.SetCursorPos(origin.x + int(x), origin.y + int(y))
            user32.PostMessageW(hwnd, WM_MOUSEMOVE, 0, lparam)
            user32.PostMessageW(hwnd, down, mk, lparam)
            time.sleep(hold)
            user32.PostMessageW(hwnd, up, 0, lparam)
            user32.SetCursorPos(orig.x, orig.y)
            return True
        except Exception:
            return False
        finally:
            try:
                user32.ReleaseCapture()
            except Exception:
                pass

    try:
        user32.PostMessageW(hwnd, WM_MOUSEMOVE, 0, lparam)
        user32.PostMessageW(hwnd, down, mk, lparam)
        time.sleep(hold)
        user32.PostMessageW(hwnd, up, 0, lparam)
        return True
    except Exception:
        return False
    finally:
        try:
            user32.ReleaseCapture()
        except Exception:
            pass


def send_scroll_bg(hwnd, x, y, direction="down", notches=1):
    """Scroll the mouse wheel at (x, y) inside the target window.
    Returns True if the scroll was sent."""
    if not WINAPI_OK or not hwnd:
        return False
    try:
        sx, sy = client_to_screen(hwnd, x, y)
        lparam = _make_lparam(sx, sy)
        delta = WHEEL_DELTA * notches if direction == "up" else -WHEEL_DELTA * notches
        wparam = _make_wheel_wparam(delta)
        user32.PostMessageW(hwnd, WM_MOUSEWHEEL, wparam, lparam)
        return True
    except Exception:
        return False


#  APP
class CoordClickerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("✧ CoordClicker ✧")
        self.root.configure(bg=C["bg"])
        self.root.geometry("480x560")
        self.root.minsize(320, 260)
        try:
            self._icon_img = tk.PhotoImage(data=ICON_PNG_B64)
            self.root.iconphoto(True, self._icon_img)
        except Exception:
            pass

        self.target_hwnd = None
        self.target_title_var = tk.StringVar(value="(none selected, required to click)")

        self.right_coord = None          # saved position, relative to the window
        self.left_coord = None
        self.right_button_var = tk.StringVar(value="Right click")
        self.left_button_var = tk.StringVar(value="Left click")
        self.amount_var = tk.StringVar(value="10")
        self.click_delay_var = tk.StringVar(value="100")  # ms between actions

        self.right_hotkey_var = tk.StringVar(value="f1")
        self.left_hotkey_var = tk.StringVar(value="f2")
        self.start_hotkey_var = tk.StringVar(value="f3")
        self.topmost_var = tk.BooleanVar(value=False)

        self._registered_hotkey_handles = []
        self._running = False
        self._stop_event = threading.Event()
        self._run_thread = None

        self._load_settings()
        self._build_ui()
        self._register_hotkeys()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # saving and loading settings
    def _load_settings(self):
        if not os.path.exists(SETTINGS_FILE):
            return
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return
        self.right_coord = tuple(data["right_coord"]) if data.get("right_coord") else None
        self.left_coord = tuple(data["left_coord"]) if data.get("left_coord") else None
        self.right_button_var.set(data.get("right_button", "Right click"))
        self.left_button_var.set(data.get("left_button", "Left click"))
        self.amount_var.set(str(data.get("amount", 10)))
        self.click_delay_var.set(str(data.get("click_delay_ms", 100)))
        self.right_hotkey_var.set(data.get("right_hotkey", "f1"))
        self.left_hotkey_var.set(data.get("left_hotkey", "f2"))
        self.start_hotkey_var.set(data.get("start_hotkey", "f3"))
        self.topmost_var.set(bool(data.get("always_on_top", False)))
        target_title = data.get("target_title")
        if target_title:
            self.target_title_var.set(f"{target_title}  (re-detects on next hotkey press)")

    def _save_settings(self):
        data = {
            "right_coord": list(self.right_coord) if self.right_coord else None,
            "left_coord": list(self.left_coord) if self.left_coord else None,
            "right_button": self.right_button_var.get(),
            "left_button": self.left_button_var.get(),
            "amount": self._safe_int(self.amount_var.get(), 10),
            "click_delay_ms": self._safe_int(self.click_delay_var.get(), 100),
            "right_hotkey": self.right_hotkey_var.get().strip() or "f1",
            "left_hotkey": self.left_hotkey_var.get().strip() or "f2",
            "start_hotkey": self.start_hotkey_var.get().strip() or "f3",
            "always_on_top": bool(self.topmost_var.get()),
            "target_title": window_title(self.target_hwnd) if is_window_valid(self.target_hwnd) else None,
        }
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    @staticmethod
    def _safe_int(s, default):
        """Turn text into a positive whole number, or use the default."""
        try:
            v = int(str(s).strip())
            return v if v > 0 else default
        except Exception:
            return default

    # building the interface
    def _build_ui(self):
        header = tk.Frame(self.root, bg=C["bg2"], height=48)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        tk.Label(header, text="✧ COORDCLICKER ✧", bg=C["bg2"], fg=C["accent"],
                 font=FONT_HEAD).pack(side="left", padx=16)

        # Scrollable area so everything stays reachable in a small window
        scroll_wrap = tk.Frame(self.root, bg=C["bg"])
        scroll_wrap.pack(fill="both", expand=True)

        canvas = tk.Canvas(scroll_wrap, bg=C["bg"], highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(scroll_wrap, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        body = tk.Frame(canvas, bg=C["bg"], padx=14, pady=12)
        body_window = canvas.create_window((0, 0), window=body, anchor="nw")

        def _sync_scrollregion(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _sync_body_width(event):
            canvas.itemconfig(body_window, width=event.width)

        body.bind("<Configure>", _sync_scrollregion)
        canvas.bind("<Configure>", _sync_body_width)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Mouse wheel only scrolls this panel while the mouse is over it
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # Target window
        tgt_card = self._card(body)
        tgt_card.pack(fill="x", pady=(0, 10))
        tk.Label(tgt_card, text="Target Window", bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(8, 2))
        row = tk.Frame(tgt_card, bg=C["panel"])
        row.pack(fill="x", padx=10, pady=(0, 10))
        self.target_lbl = tk.Label(row, textvariable=self.target_title_var,
                                    bg=C["panel2"], fg=C["muted"], font=FONT_SMALL,
                                    anchor="w", padx=8, pady=6)
        self.target_lbl.pack(side="left", fill="x", expand=True)
        self._btn(row, "Pick…", self._open_window_picker, width=8).pack(side="left", padx=(6, 0))
        self._btn(row, "Clear", self._clear_target, color=C["muted"], fg="#0a1420",
                   width=6).pack(side="left", padx=(6, 0))
        tk.Label(tgt_card, text="The window under your mouse when you press a coord "
                                 "hotkey becomes the target. Use \"Pick…\" to choose "
                                 "one by hand instead.",
                 bg=C["panel"], fg=C["muted"], font=("Segoe UI", 8), wraplength=430,
                 justify="left").pack(anchor="w", padx=10, pady=(0, 8))

        # Coordinates
        coord_card = self._card(body)
        coord_card.pack(fill="x", pady=(0, 10))
        tk.Label(coord_card, text="Coordinates", bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(8, 4))

        self.right_row_lbl = self._build_coord_row(
            coord_card, "Right", self.right_hotkey_var, self.right_button_var,
            self._set_right_coord)
        self.left_row_lbl = self._build_coord_row(
            coord_card, "Left", self.left_hotkey_var, self.left_button_var,
            self._set_left_coord)
        tk.Frame(coord_card, bg=C["panel"], height=6).pack()

        # Amount and delay
        amt_card = self._card(body)
        amt_card.pack(fill="x", pady=(0, 10))
        tk.Label(amt_card, text="Click Pattern", bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(8, 4))
        amt_row = tk.Frame(amt_card, bg=C["panel"])
        amt_row.pack(fill="x", padx=10, pady=(0, 4))
        tk.Label(amt_row, text="Clicks on Right before moving to Left:",
                 bg=C["panel"], fg=C["muted"], font=FONT_SMALL).pack(side="left")
        amt_entry = tk.Entry(amt_row, textvariable=self.amount_var, width=5,
                              justify="center", bg=C["panel2"], fg=C["text"],
                              insertbackground=C["text"], relief="flat")
        amt_entry.pack(side="left", padx=8)

        delay_row = tk.Frame(amt_card, bg=C["panel"])
        delay_row.pack(fill="x", padx=10, pady=(0, 10))
        tk.Label(delay_row, text="Delay between clicks (ms):",
                 bg=C["panel"], fg=C["muted"], font=FONT_SMALL).pack(side="left")
        delay_entry = tk.Entry(delay_row, textvariable=self.click_delay_var, width=5,
                                justify="center", bg=C["panel2"], fg=C["text"],
                                insertbackground=C["text"], relief="flat")
        delay_entry.pack(side="left", padx=8)

        tk.Label(amt_card, text="Loop: click Right N times -> click Left once -> repeat.",
                 bg=C["panel"], fg=C["muted"], font=("Segoe UI", 8)).pack(
            anchor="w", padx=10, pady=(0, 8))

        # Start / Stop
        start_card = self._card(body)
        start_card.pack(fill="x", pady=(0, 10))
        tk.Label(start_card, text="Start / Stop", bg=C["panel"], fg=C["text"],
                 font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=10, pady=(8, 4))
        st_row = tk.Frame(start_card, bg=C["panel"])
        st_row.pack(fill="x", padx=10, pady=(0, 4))
        tk.Label(st_row, text="Hotkey:", bg=C["panel"], fg=C["muted"],
                 font=FONT_SMALL).pack(side="left")
        self._hotkey_capture_entry(st_row, self.start_hotkey_var, self._register_hotkeys)
        self.start_btn = self._btn(start_card, "▶  Start", self._toggle_running,
                                    color=C["green"], width=14)
        self.start_btn.pack(padx=10, pady=(4, 4), anchor="w")

        def _apply_topmost():
            self.root.attributes("-topmost", bool(self.topmost_var.get()))
            self._save_settings()

        tk.Checkbutton(start_card, text="Keep this window on top",
                       variable=self.topmost_var, command=_apply_topmost,
                       bg=C["panel"], fg=C["muted"], selectcolor=C["panel2"],
                       activebackground=C["panel"], activeforeground=C["text"],
                       font=FONT_SMALL, bd=0, highlightthickness=0).pack(
            padx=10, pady=(0, 10), anchor="w")
        self.root.attributes("-topmost", bool(self.topmost_var.get()))

        # Status bar
        self.status_var = tk.StringVar(value="idle")
        status = tk.Frame(self.root, bg=C["bg2"], height=26)
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)
        kb_txt = "keyboard✓" if KEYBOARD_OK else "keyboard✗ (pip install keyboard for hotkeys)"
        win_txt = "winapi✓" if WINAPI_OK else "winapi✗ (Windows required)"
        tk.Label(status, textvariable=self.status_var, bg=C["bg2"], fg=C["muted"],
                 font=FONT_SMALL).pack(side="left", padx=12)
        tk.Label(status, text=f"{win_txt}   {kb_txt}", bg=C["bg2"], fg=C["muted"],
                 font=FONT_SMALL).pack(side="right", padx=12)

        self._refresh_coord_labels()

    def _build_coord_row(self, parent, label, hotkey_var, button_var, on_set):
        row = tk.Frame(parent, bg=C["panel"])
        row.pack(fill="x", padx=10, pady=(4, 0))
        tk.Label(row, text=f"{label}:", bg=C["panel"], fg=C["text"], width=6,
                 anchor="w", font=FONT_BODY).pack(side="left")
        coord_lbl = tk.Label(row, text="not set", bg=C["panel2"], fg=C["muted"],
                              font=FONT_MONO, width=16, anchor="w", padx=6)
        coord_lbl.pack(side="left", padx=(0, 8))
        tk.Label(row, text="Hotkey:", bg=C["panel"], fg=C["muted"],
                 font=FONT_SMALL).pack(side="left")
        self._hotkey_capture_entry(row, hotkey_var, self._register_hotkeys)
        self._btn(row, "Set now", on_set, width=9).pack(side="left", padx=(6, 0))

        sub_row = tk.Frame(parent, bg=C["panel"])
        sub_row.pack(fill="x", padx=10, pady=(2, 6))
        tk.Label(sub_row, text="", width=6, bg=C["panel"]).pack(side="left")
        tk.Label(sub_row, text="Action:", bg=C["panel"], fg=C["muted"],
                 font=FONT_SMALL).pack(side="left")
        btn_menu = ttk.Combobox(sub_row, textvariable=button_var, state="readonly",
                                 values=["Left click", "Right click",
                                         "Scroll Down", "Scroll Up"], width=11,
                                 font=FONT_SMALL)
        btn_menu.pack(side="left", padx=(6, 0))
        btn_menu.bind("<<ComboboxSelected>>", lambda e: self._save_settings())
        return coord_lbl

    def _hotkey_capture_entry(self, parent, var, on_change):
        entry = tk.Entry(parent, textvariable=var, width=12, justify="center",
                          bg=C["panel2"], fg=C["accent"], insertbackground=C["text"],
                          relief="flat")
        entry.pack(side="left", padx=(6, 0))

        def capture():
            # The keyboard button: press your key combo and it gets recorded
            if not KEYBOARD_OK:
                messagebox.showwarning(
                    "keyboard not installed",
                    "Install the 'keyboard' package to use hotkeys:\n\n"
                    "pip install keyboard")
                return
            entry.delete(0, tk.END)
            entry.insert(0, "press keys…")
            entry.update()

            def worker():
                combo = kb.read_hotkey(suppress=False)
                self.root.after(0, lambda: (var.set(combo), on_change()))

            threading.Thread(target=worker, daemon=True).start()

        self._btn(parent, "🎹", capture, width=3).pack(side="left", padx=(4, 0))

    def _card(self, parent):
        f = tk.Frame(parent, bg=C["panel"], highlightbackground=C["border"],
                     highlightthickness=1)
        return f

    def _btn(self, parent, text, command, color=None, fg=None, width=10):
        return tk.Button(parent, text=text, command=command,
                          bg=color or C["accent"], fg=fg or "#0a1420",
                          activebackground=color or C["accent"],
                          relief="flat", font=FONT_SMALL, width=width,
                          cursor="hand2", bd=0, padx=4, pady=3)

    # choosing the target window
    def _open_window_picker(self):
        if not WINAPI_OK:
            messagebox.showwarning("Missing", "Windows API not available. "
                                               "This only works on Windows.")
            return
        windows = scan_windows()
        if not windows:
            messagebox.showinfo("No windows found", "Nothing visible was found to pick.")
            return
        popup = tk.Toplevel(self.root)
        popup.title("Pick target window")
        popup.configure(bg=C["panel"])
        popup.geometry("360x420")
        popup.transient(self.root)
        popup.grab_set()

        listbox = tk.Listbox(popup, bg=C["panel2"], fg=C["text"],
                              selectbackground=C["accent"], font=FONT_BODY,
                              relief="flat", highlightthickness=0)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        for hwnd, title in windows:
            listbox.insert(tk.END, title)

        def choose():
            sel = listbox.curselection()
            if not sel:
                return
            hwnd, title = windows[sel[0]]
            self.target_hwnd = hwnd
            self.target_title_var.set(title)
            popup.destroy()

        listbox.bind("<Double-Button-1>", lambda e: choose())
        self._btn(popup, "Select", choose, width=12).pack(pady=(0, 10))

    def _clear_target(self):
        self.target_hwnd = None
        self.target_title_var.set("(none selected, required to click)")

    # saving coordinates
    def _capture_relative_point(self):
        """Read the mouse position, work out which window it is over,
        make that window the target, and return the position relative
        to it."""
        x, y = get_cursor_pos()
        hwnd = window_from_point(x, y)
        if not (hwnd and is_window_valid(hwnd)):
            return None, None
        self.target_hwnd = hwnd
        self.target_title_var.set(window_title(hwnd) or "(unnamed window)")
        return hwnd, screen_to_client(hwnd, x, y)

    def _set_right_coord(self):
        hwnd, pt = self._capture_relative_point()
        if pt is None:
            self.status_var.set("Couldn't detect a window under the cursor")
            return
        self.right_coord = pt
        self._refresh_coord_labels()
        self._save_settings()
        self.status_var.set(f"Right coord set: {self.right_coord}  on '{window_title(hwnd)}'")

    def _set_left_coord(self):
        hwnd, pt = self._capture_relative_point()
        if pt is None:
            self.status_var.set("Couldn't detect a window under the cursor")
            return
        self.left_coord = pt
        self._refresh_coord_labels()
        self._save_settings()
        self.status_var.set(f"Left coord set: {self.left_coord}  on '{window_title(hwnd)}'")

    def _refresh_coord_labels(self):
        self.right_row_lbl.config(
            text=str(self.right_coord) if self.right_coord else "not set",
            fg=C["green"] if self.right_coord else C["muted"])
        self.left_row_lbl.config(
            text=str(self.left_coord) if self.left_coord else "not set",
            fg=C["green"] if self.left_coord else C["muted"])

    # hotkeys
    def _register_hotkeys(self):
        if not KEYBOARD_OK:
            self.status_var.set("keyboard package not installed, hotkeys inactive")
            return
        # Remove the old hotkeys first, then add the current ones
        for h in self._registered_hotkey_handles:
            try:
                kb.remove_hotkey(h)
            except Exception:
                pass
        self._registered_hotkey_handles = []

        def register(combo, callback):
            combo = (combo or "").strip()
            if not combo:
                return
            try:
                handle = kb.add_hotkey(combo, lambda: self.root.after(0, callback))
                self._registered_hotkey_handles.append(handle)
            except Exception:
                pass

        register(self.right_hotkey_var.get(), self._set_right_coord)
        register(self.left_hotkey_var.get(), self._set_left_coord)
        register(self.start_hotkey_var.get(), self._toggle_running)
        self._save_settings()
        self.status_var.set("hotkeys registered")

    # the click loop
    def _toggle_running(self):
        if self._running:
            self._stop_running()
        else:
            self._start_running()

    def _start_running(self):
        if not self.target_hwnd or not is_window_valid(self.target_hwnd):
            messagebox.showwarning("No target window",
                                    "Pick a target window first (or press a coord "
                                    "hotkey while your mouse is over it).")
            return
        if not self.right_coord or not self.left_coord:
            messagebox.showwarning("Missing coordinates",
                                    "Set both the Right and Left coordinates first.")
            return
        if not WINAPI_OK:
            messagebox.showwarning("Missing", "Windows API not available. "
                                               "This only works on Windows.")
            return
        self._running = True
        self._stop_event = threading.Event()
        self._save_settings()
        self.start_btn.config(text="■  Stop", bg=C["red"])
        self._run_thread = threading.Thread(target=self._run_loop,
                                            args=(self._stop_event,), daemon=True)
        self._run_thread.start()

    def _stop_running(self):
        self._running = False
        self._stop_event.set()
        self.start_btn.config(text="▶  Start", bg=C["green"])
        self.status_var.set("stopped")

    @staticmethod
    def _action_kind(button_var):
        """Turn the dropdown text into an action name."""
        v = button_var.get().strip().lower()
        if v.startswith("right"):
            return "right"
        if v.startswith("scroll down"):
            return "scroll_down"
        if v.startswith("scroll up"):
            return "scroll_up"
        return "left"

    @staticmethod
    def _send_action(hwnd, x, y, kind):
        if kind == "scroll_down":
            return send_scroll_bg(hwnd, x, y, direction="down")
        if kind == "scroll_up":
            return send_scroll_bg(hwnd, x, y, direction="up")
        return send_click_bg(hwnd, x, y, button=kind)

    @staticmethod
    def _action_label(kind):
        return {"scroll_down": "scroll-down", "scroll_up": "scroll-up",
                "left": "left-click", "right": "right-click"}.get(kind, kind)

    def _run_loop(self, stop):
        """Runs in a background thread. `stop` is this run's own stop flag,
        so an old run can never interfere with a newly started one."""
        amount = self._safe_int(self.amount_var.get(), 10)
        delay_s = self._safe_int(self.click_delay_var.get(), 100) / 1000
        right_kind = self._action_kind(self.right_button_var)
        left_kind = self._action_kind(self.left_button_var)
        right_label = self._action_label(right_kind)
        left_label = self._action_label(left_kind)
        total = 0
        final_msg = "idle"
        self.root.after(0, lambda: self.status_var.set("running…"))
        while not stop.is_set():
            hwnd = self.target_hwnd
            if not is_window_valid(hwnd):
                final_msg = "target window closed, stopped"
                break
            rx, ry = self.right_coord
            for i in range(amount):
                if stop.is_set():
                    break
                self._send_action(hwnd, rx, ry, right_kind)
                total += 1
                self.root.after(0, lambda i=i, t=total: self.status_var.set(
                    f"running… right {right_label} {i + 1}/{amount}  (total {t})"))
                # wait() returns early when Stop is pressed, so stopping is instant
                if stop.wait(delay_s):
                    break
            if stop.is_set():
                break
            lx, ly = self.left_coord
            self._send_action(hwnd, lx, ly, left_kind)
            total += 1
            self.root.after(0, lambda t=total: self.status_var.set(
                f"running… left {left_label}  (total {t})"))
            stop.wait(delay_s)
        if stop is self._stop_event:
            self._running = False
            self.root.after(0, lambda: self.start_btn.config(text="▶  Start", bg=C["green"]))
            self.root.after(0, lambda: self.status_var.set(
                f"{final_msg}  (total {total})" if total else final_msg))

    # closing the app
    def _on_close(self):
        self._stop_event.set()
        if KEYBOARD_OK:
            for h in self._registered_hotkey_handles:
                try:
                    kb.remove_hotkey(h)
                except Exception:
                    pass
        self._save_settings()
        self.root.destroy()


def _enable_dpi_awareness():
    """Makes Windows report real pixel positions on scaled displays
    (125%, 150% and so on), so saved coordinates land where you expect."""
    if not WINAPI_OK:
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass


def _hide_console():
    """Hide the black console window when launched from a terminal,
    so only the app window shows."""
    if not WINAPI_OK:
        return
    try:
        kernel32 = ctypes.windll.kernel32
        console_hwnd = kernel32.GetConsoleWindow()
        if not console_hwnd:
            return
        kernel32.FreeConsole()
        if user32.IsWindow(console_hwnd):
            SW_HIDE = 0
            user32.ShowWindow(console_hwnd, SW_HIDE)
    except Exception:
        pass


if __name__ == "__main__":
    _hide_console()
    _enable_dpi_awareness()
    root = tk.Tk()
    app = CoordClickerApp(root)
    root.mainloop()
