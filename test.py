import tkinter as tk
import time
import threading
import win32gui
import win32process
import psutil
import os
from PIL import Image, ImageTk

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

        # Pillow用の木とリンゴ画像をRGBAでロード
        self.tree_img = Image.open(os.path.join(img_dir, "tree.png")).convert("RGBA")
        apple_original = Image.open(os.path.join(img_dir, "apple.png")).convert("RGBA")

        # リンゴ画像を4分の1サイズに縮小
        w, h = apple_original.size
        self.apple_img = apple_original.resize((w // 4, h // 4), Image.LANCZOS)

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
        # 経過時間に応じて通常画像またはリンゴ付きの木を表示
        if self.time_elapsed < 10:
            self.image_label.config(image=self.images["1"])
        elif self.time_elapsed < 20:
            self.image_label.config(image=self.images["2"])
        elif self.time_elapsed < 40:
            self.image_label.config(image=self.images["3"])
        else:
            # 40秒以降は木＋リンゴを表示（最初は両方透明）
            self.display_tree_with_apples()
            
    def adjust_image_opacity(img: Image.Image, opacity: float) -> Image.Image:
    # 画像の透明度を調整（既存の透過は維持しつつ全体をフェード）
    assert 0.0 <= opacity <= 1.0, "opacity must be between 0 and 1"
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    alpha = img.split()[3]
    new_alpha = alpha.point(lambda p: int(p * opacity))
    img.putalpha(new_alpha)
    return img


    def display_tree_with_apples(self):
        # 木のコピーを作成
        tree = self.tree_img.copy()

        # リンゴを置く座標
        positions = [(50, 50), (150, 80)]

        # 40秒〜50秒の間はリンゴ透明（alpha=0）
        # 50秒以降、1つ目のリンゴだけ表示（alpha=255）
        for i, pos in enumerate(positions):
            apple = self.apple_img.copy()
            if self.time_elapsed < 50:
                apple.putalpha(0)  # 完全透明
            else:
                if i == 0:
                    apple.putalpha(255)  # 表示
                else:
                    apple.putalpha(0)  # 透明
            tree.alpha_composite(apple, dest=pos)

        # Tkinter表示用に変換
        tk_image = ImageTk.PhotoImage(tree)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image  # GC対策

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTimeApp(root)
    root.mainloop()
