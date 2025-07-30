import tkinter as tk
import time
import threading
import win32gui
import win32process
import psutil
import os

class ScreenTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("スクリーンタイム計測＋画像表示")

        self.time_elapsed = 0  # 秒数
        self.last_check = time.time()
        self.running = False
        self.started = False

        # タイマー表示
        self.label = tk.Label(root, text="00:00:00", font=("Helvetica", 32))
        self.label.pack(pady=10)

        # ステータス表示
        self.status_label = tk.Label(root, text="停止中", font=("Helvetica", 14), fg="gray")
        self.status_label.pack()

        # 画像表示用ラベル
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        # "img" フォルダ内の画像をロード
        img_dir = os.path.join(os.getcwd(), "img")
        self.images = {
            "1": tk.PhotoImage(file=os.path.join(img_dir, "1.png")),
            "2": tk.PhotoImage(file=os.path.join(img_dir, "2.png")),
            "3": tk.PhotoImage(file=os.path.join(img_dir, "3.png"))
        }

        # デフォルトで1.pngを表示
        self.image_label.config(image=self.images["1"])

        # スタートボタン
        self.start_button = tk.Button(root, text="スタート", command=self.start_timer)
        self.start_button.pack(pady=5)

        # タイマー更新スレッド
        self.update_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.update_thread.start()

    def start_timer(self):
        self.started = True
        self.last_check = time.time()
        self.start_button.config(state="disabled")
        self.status_label.config(text="停止中", fg="gray")

    def is_browser_active(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            name = process.name().lower()
            # 対象アプリ
            return name in ['chrome.exe', 'msedge.exe', 'winword.exe', 'excel.exe', 'zotero.exe', 'code.exe']
        except Exception:
            return False

    def update_timer(self):
        while True:
            time.sleep(1)
            now = time.time()

            if not self.started:
                self.last_check = now
                continue

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
            self.update_image()  # 時間ごとに画像を切り替え

    def update_label(self):
        hrs, rem = divmod(self.time_elapsed, 3600)
        mins, secs = divmod(rem, 60)
        self.label.config(text=f"{hrs:02}:{mins:02}:{secs:02}")

    def update_image(self):
        # 経過時間に応じて画像を切り替え
        if self.time_elapsed < 10:
            self.image_label.config(image=self.images["1"])
        elif self.time_elapsed < 20:
            self.image_label.config(image=self.images["2"])
        else:
            self.image_label.config(image=self.images["3"])

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTimeApp(root)
    root.mainloop()
