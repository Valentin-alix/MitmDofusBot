from asyncio import Event
from dataclasses import dataclass, field

import win32api
import win32con
import win32gui

from databases.database import Database


@dataclass
class BotClick:
    database: Database
    nickname: str
    event_ready: Event
    event_is_playing: Event
    windows_name: str = field(default=None, init=False)
    hwnd: int = field(default=None, init=False)

    def click(self, l_param: win32api.MAKELONG):
        win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, l_param)
        win32gui.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, None, l_param)

    def find_windows_name(self) -> None:
        def win_enum_handler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                if self.nickname in win32gui.GetWindowText(hwnd):
                    self.windows_name = win32gui.GetWindowText(hwnd)

        win32gui.EnumWindows(win_enum_handler, None)
