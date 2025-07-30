import tkinter as tk
import time
import threading
import win32gui
import win32process
import psutil
import os
import random
from PIL import Image, ImageTk

class ScreenTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("やる木")

        self.time_elapsed = 0
        self.last_check = time.time()
        self.running = False
        self.started = False

        # 時間表示ラベル
        self.label = tk.Label(root, text="00:00:00", font=("Helvetica", 32))
        self.label.pack(pady=10)

        self.status_label = tk.Label(root, text="今日も頑張ろうね^^", font=("Helvetica", 14), fg="gray")
        self.status_label.pack()

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        img_dir = os.path.join(os.getcwd(), "img")

        self.images = {}

        tree4_path = os.path.join(img_dir, "tree4.png")
        self.tree_img = Image.open(tree4_path).convert("RGBA")
        self.tree_img = self.tree_img.resize((self.tree_img.width // 10, self.tree_img.height // 10), Image.LANCZOS)
        tree4_height = self.tree_img.height

        def load_and_align_tree(img_path, scale_divisor):
            img = Image.open(img_path).convert("RGBA")
            resized = img.resize((img.width // scale_divisor, img.height // scale_divisor), Image.LANCZOS)
            canvas = Image.new("RGBA", (resized.width, tree4_height), (255, 255, 255, 0))
            y_offset = tree4_height - resized.height
            canvas.paste(resized, (0, y_offset), resized)
            return ImageTk.PhotoImage(canvas)

        self.images["1"] = load_and_align_tree(os.path.join(img_dir, "tree1.png"), 5)
        self.images["2"] = load_and_align_tree(os.path.join(img_dir, "tree2.png"), 8)
        self.images["3"] = load_and_align_tree(os.path.join(img_dir, "tree3.png"), 8)

        self.apple_images = {
            'R': Image.open(os.path.join(img_dir, "apple_red.png")).convert("RGBA"),
            'G': Image.open(os.path.join(img_dir, "apple_green.png")).convert("RGBA"),
            'B': Image.open(os.path.join(img_dir, "apple_blue.png")).convert("RGBA")
        }
        for key in self.apple_images:
            img = self.apple_images[key]
            self.apple_images[key] = img.resize((img.width // 20, img.height // 20), Image.LANCZOS)

        self.image_label.config(image=self.images["1"])

        self.group_canvas = tk.Canvas(root, height=120)
        self.group_frame = tk.Frame(self.group_canvas)
        self.scrollbar = tk.Scrollbar(root, orient="horizontal", command=self.group_canvas.xview)
        self.group_canvas.configure(xscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="bottom", fill="x")
        self.group_canvas.pack(side="bottom", fill="x")
        self.group_canvas.create_window((0, 0), window=self.group_frame, anchor="nw")

        self.group_titles = {
            'R': "調べた時間",
            'B': "まとめた時間",
            'G': "分析時間"
        }

        self.group_colors = {
            'R': "red",
            'B': "blue",
            'G': "green"
        }

        self.group_labels = {}
        for key, title in self.group_titles.items():
            lbl = tk.Label(self.group_frame, text=f"{title}: 00:00:00", font=("Helvetica", 14), fg=self.group_colors[key])
            lbl.pack(anchor="w", pady=3)
            self.group_labels[key] = lbl

        self.group_frame.bind("<Configure>", lambda e: self.group_canvas.configure(scrollregion=self.group_canvas.bbox("all")))

        # ボタンを横並びにするフレーム
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=5)

        self.start_button = tk.Button(self.button_frame, text="START", command=self.start_timer)
        self.start_button.pack(side="left", padx=5)

        self.reset_button = tk.Button(self.button_frame, text="リセット", command=self.reset_timer)
        self.reset_button.pack(side="left", padx=5)

        self.update_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.update_thread.start()

        self.app_group_map = {
            'chrome.exe': 'R',
            'msedge.exe': 'R',
            'zotero.exe': 'R',
            'winword.exe': 'B',
            'powerpnt.exe': 'B',
            'excel.exe': 'G',
            'code.exe': 'G',
        }

        self.group_times = {'R': 0, 'B': 0, 'G': 0}
        self.apple_positions = [
            (149, 178), (275, 106), (111, 65), (240, 157),
            (182, 212), (290, 51), (208, 88), (129, 236), (171, 62)
        ]
        self.apple_drawn = []

    def start_timer(self):
        self.started = True
        self.last_check = time.time()
        self.start_button.config(state="disabled")
        self.status_label.config(text="木を成長させよう！", fg="gray")

    def reset_timer(self):
        self.time_elapsed = 0
        self.group_times = {'R': 0, 'B': 0, 'G': 0}
        self.apple_drawn = []
        self.started = False
        self.running = False
        self.start_button.config(state="normal")
        self.status_label.config(text="今日も頑張ろうね^^", fg="gray")
        self.update_label()
        self.update_group_labels()
        self.image_label.config(image=self.images["1"])
        self.image_label.image = self.images["1"]

    def get_active_process_name(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return psutil.Process(pid).name().lower()
        except Exception:
            return None

    def update_timer(self):
        while True:
            time.sleep(1)
            now = time.time()

            if not self.started:
                self.last_check = now
                continue

            elapsed = int(now - self.last_check)
            self.last_check = now

            process_name = self.get_active_process_name()
            group = self.app_group_map.get(process_name, None)

            if group:
                if not self.running:
                    self.status_label.config(text="木が成長中...", fg="green")
                self.time_elapsed += elapsed
                self.group_times[group] += elapsed
                self.running = True
            else:
                if self.running:
                    self.status_label.config(text="休憩中", fg="gray")
                self.running = False

            self.update_label()
            self.update_group_labels()
            self.update_image()

    def update_group_labels(self):
        for group, seconds in self.group_times.items():
            hrs, rem = divmod(seconds, 3600)
            mins, secs = divmod(rem, 60)
            title = self.group_titles[group]
            self.group_labels[group].config(text=f"{title}: {hrs:02}:{mins:02}:{secs:02}")

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
        positions_pool = [pos for pos in self.apple_positions if pos not in [p[1] for p in self.apple_drawn]]

        for group in ['R', 'G', 'B']:
            count = self.group_times[group] // 30
            existing = sum(1 for g, _ in self.apple_drawn if g == group)
            to_add = count - existing

            for _ in range(to_add):
                if not positions_pool:
                    break
                pos = positions_pool.pop()
                self.apple_drawn.append((group, pos))

        for group, pos in self.apple_drawn:
            apple = self.apple_images[group].copy()
            tree.alpha_composite(apple, dest=pos)

        tk_image = ImageTk.PhotoImage(tree)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTimeApp(root)
    root.mainloop()
