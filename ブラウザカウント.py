import tkinter as tk
import time
import threading
import win32gui
import win32process
import psutil

class ScreenTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ブラウザスクリーンタイム計測")

        self.time_elapsed = 0  # 秒数
        self.last_check = time.time()
        self.running = False  # 内部的なフラグ（今カウントしてるか）

        self.label = tk.Label(root, text="00:00:00", font=("Helvetica", 32))
        self.label.pack(pady=20)

        # ステータス表示ラベル（カウント中か停止中か）
        self.status_label = tk.Label(root, text="停止中", font=("Helvetica", 14), fg="gray")
        self.status_label.pack()

        self.update_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.update_thread.start()

    def is_browser_active(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            name = process.name().lower()

            # Chrome または Edge に限定
            return name in ['chrome.exe', 'msedge.exe']
        except Exception:
            return False

    def update_timer(self):
        while True:
            time.sleep(1)
            now = time.time()
            active = self.is_browser_active()

            if active:
                if not self.running:
                    self.status_label.config(text="カウント中", fg="green")
                    self.last_check = now  # 初回カウント時に時刻をリセット
                self.time_elapsed += int(now - self.last_check)
                self.running = True
            else:
                if self.running:
                    self.status_label.config(text="停止中", fg="gray")
                self.running = False

            self.last_check = now
            self.update_label()

    def update_label(self):
        hrs, rem = divmod(self.time_elapsed, 3600)
        mins, secs = divmod(rem, 60)
        time_str = f"{hrs:02}:{mins:02}:{secs:02}"
        self.label.config(text=time_str)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTimeApp(root)
    root.mainloop()
