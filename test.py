import tkinter as tk
import time
import threading
import ctypes
from ctypes import wintypes

# Windowsのメッセージ定義
WM_POWERBROADCAST = 0x0218
PBT_APMSUSPEND = 0x0004      # スリープへ移行
PBT_APMRESUMEAUTOMATIC = 0x0012  # 復帰

# ウィンドウプロシージャ型
WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int)

class ScreenTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("スクリーンタイム計測")

        self.time_elapsed = 0
        self.running = False
        self.last_check = time.time()
        self.suspended = False  # スリープ中かどうか

        self.label = tk.Label(root, text="00:00:00", font=("Helvetica", 32))
        self.label.pack(pady=20)

        self.start_button = tk.Button(root, text="スタート", command=self.start_timer)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="ストップ", command=self.stop_timer, state="disabled")
        self.stop_button.pack(pady=5)

        # Windowsメッセージフック設定
        self.old_proc = None
        self._setup_message_hook()

        # タイマー更新スレッド
        self.update_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.update_thread.start()

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
        time_str = f"{hrs:02}:{mins:02}:{secs:02}"
        self.label.config(text=time_str)

    def _setup_message_hook(self):
        # Tkinterウィンドウのハンドルを取得
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())

        # カスタムプロシージャ
        def winproc(hwnd, msg, wparam, lparam):
            if msg == WM_POWERBROADCAST:
                if wparam == PBT_APMSUSPEND:
                    print("スリープ検出：計測停止")
                    self.suspended = True
                elif wparam == PBT_APMRESUMEAUTOMATIC:
                    print("復帰検出：計測再開")
                    self.suspended = False
            return ctypes.windll.user32.CallWindowProcW(self.old_proc, hwnd, msg, wparam, lparam)

        # 関数ポインタを作成
        self.proc = WNDPROC(winproc)

        # 元のウィンドウプロシージャを取得して置き換え
        self.old_proc = ctypes.windll.user32.SetWindowLongPtrW(hwnd, -4, self.proc)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTimeApp(root)
    root.mainloop()
