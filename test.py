import tkinter as tk
import time
import threading
import win32gui
import win32process
import psutil
import os
from PIL import Image, ImageTk  # Pillowで透明度処理

class ScreenTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("スクリーンタイム計測＋リンゴの木")

        self.time_elapsed = 0
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

        # Pillow用の木とリンゴ画像もロード
        self.tree_img = Image.open(os.path.join(img_dir, "tree.png")).convert("RGBA")
        self.apple_img = Image.open(os.path.join(img_dir, "apple.png")).convert("RGBA")
        
        # 木の画像を2倍に拡大（任意の倍率に変更可能）
        self.tree_img = self.tree_img.resize(
            (self.tree_img.width * 2, self.tree_img.height * 2), Image.LANCZOS
        )

        # リンゴもサイズ縮小（8分の1）
        self.apple_img = self.apple_img.resize(
            (self.apple_img.width // 8, self.apple_img.height // 8), Image.LANCZOS
        )

        # デフォルト画像を表示
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
            self.update_image()

    def update_label(self):
        hrs, rem = divmod(self.time_elapsed, 3600)
        mins, secs = divmod(rem, 60)
        self.label.config(text=f"{hrs:02}:{mins:02}:{secs:02}")

    def update_image(self):
        if self.time_elapsed < 5:
            self.image_label.config(image=self.images["1"])
        elif self.time_elapsed < 10:
            self.image_label.config(image=self.images["2"])
        elif self.time_elapsed < 15:
            self.image_label.config(image=self.images["3"])
        else:
            self.display_tree_with_apples()

    def display_tree_with_apples(self):
        tree = self.tree_img.copy()
        positions = [(50, 50), (150, 80)]

        for i, pos in enumerate(positions):
            apple = self.apple_img.copy()

            # チャンネルを分割
            r, g, b, a = apple.split()

            if self.time_elapsed >= 20 and i == 0:
                # 1つ目のリンゴを表示（元の透過情報を使う）
                alpha = a
            else:
                # その他は完全透明
                alpha = Image.new("L", apple.size, 0)

            # アルファチャンネルを適用
            apple.putalpha(alpha)

            # 木にリンゴを合成
            tree.alpha_composite(apple, dest=pos)

        tk_image = ImageTk.PhotoImage(tree)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image  # GC防止用参照保持

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTimeApp(root)
    root.mainloop()
