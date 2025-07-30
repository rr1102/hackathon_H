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
        self.running = False  # 内部フラグ：計測中かどうか（ブラウザアクティブか）
        self.started = False  # ユーザーがスタートを押したかどうか

        # タイマー表示
        self.label = tk.Label(root, text="00:00:00", font=("Helvetica", 32))
        self.label.pack(pady=20)

        # ステータス表示
        self.status_label = tk.Label(root, text="停止中", font=("Helvetica", 14), fg="gray")
        self.status_label.pack()

        # スタート・ストップボタン
        self.start_button = tk.Button(root, text="スタート", command=self.start_timer)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="ストップ", command=self.stop_timer, state="disabled")
        self.stop_button.pack(pady=5)

        # タイマー更新スレッド
        self.update_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.update_thread.start()

    def start_timer(self):
        self.started = True
        self.last_check = time.time()
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.status_label.config(text="停止中", fg="gray")

    def stop_timer(self):
        self.started = False
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.status_label.config(text="停止中", fg="gray")

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

            # スタートボタンが押されていなければ何もしない
            if not self.started:
                self.last_check = now
                continue

            # ブラウザがアクティブかどうかチェック
            active = self.is_browser_active()

            if active:
                if not self.running:
                    self.status_label.config(text="カウント中", fg="green")
                    self.last_check = now
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
