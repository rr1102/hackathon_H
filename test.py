import tkinter as tk
import time
import threading
import win32con
import win32gui
import win32api

WM_POWERBROADCAST = 0x0218
PBT_APMSUSPEND = 0x0004
PBT_APMRESUMEAUTOMATIC = 0x0012

class ScreenTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("スクリーンタイム計測")

        self.time_elapsed = 0
        self.running = False
        self.suspended = False
        self.last_check = time.time()

        self.label = tk.Label(root, text="00:00:00", font=("Helvetica", 32))
        self.label.pack(pady=20)

        self.start_button = tk.Button(root, text="スタート", command=self.start_timer)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="ストップ", command=self.stop_timer, state="disabled")
        self.stop_button.pack(pady=5)

        # タイマー更新スレッド
        self.update_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.update_thread.start()

        # 電源イベント監視スレッド
        self.power_thread = threading.Thread(target=self.monitor_power_events, daemon=True)
        self.power_thread.start()

    def start_timer(self):
        self.running = True
        self.last_check = time.time()
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")

    def stop_timer(self):
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def update_timer(self):
        while True:
            time.sleep(1)
            if self.running and not self.suspended:
                now = time.time()
                self.time_elapsed += int(now - self.last_check)
                self.last_check = now
                self.update_label()
            else:
                self.last_check = time.time()

    def update_label(self):
        hrs, rem = divmod(self.time_elapsed, 3600)
        mins, secs = divmod(rem, 60)
        self.label.config(text=f"{hrs:02}:{mins:02}:{secs:02}")

    def monitor_power_events(self):
        # 隠しウィンドウ作成
        class_name = "HiddenPowerEventWindow"
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self._wnd_proc
        wc.lpszClassName = class_name
        wc.hInstance = win32api.GetModuleHandle(None)
        win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindow(class_name, None, 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)

        # メッセージループ
        win32gui.PumpMessages()

    def _wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == WM_POWERBROADCAST:
            if wparam == PBT_APMSUSPEND:
                print("スリープ検出: 計測停止")
                self.suspended = True
            elif wparam == PBT_APMRESUMEAUTOMATIC:
                print("復帰検出: 計測再開")
                self.suspended = False
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTimeApp(root)
    root.mainloop()
