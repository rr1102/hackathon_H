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
        self.root.title("やる木")

        self.time_elapsed = 0
        self.last_check = time.time()
        self.running = False
        self.started = False

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

        # リンゴ画像を読み込み
        self.apple_images = {
            'R': Image.open(os.path.join(img_dir, "apple_red.png")).convert("RGBA"),
            'G': Image.open(os.path.join(img_dir, "apple_green.png")).convert("RGBA"),
            'B': Image.open(os.path.join(img_dir, "apple_blue.png")).convert("RGBA")
        }
        for key in self.apple_images:
            self.apple_images[key] = self.apple_images[key].resize(
                (self.apple_images[key].width // 20, self.apple_images[key].height // 20), Image.LANCZOS
            )

        self.apple_positions = [
            (80, 30), (130, 50), (100, 70),
            (160, 40), (60, 60), (140, 90),
            (110, 20), (90, 80), (150, 60)
        ]
        self.used_positions = []
        self.apple_drops = []  # [(group, position)]

        self.image_label.config(image=self.images["1"])

        self.group_canvas = tk.Canvas(root, height=100)
        self.group_frame = tk.Frame(self.group_canvas)
        self.scrollbar = tk.Scrollbar(root, orient="horizontal", command=self.group_canvas.xview)
        self.group_canvas.configure(xscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="bottom", fill="x")
        self.group_canvas.pack(side="bottom", fill="x")
        self.group_canvas.create_window((0, 0), window=self.group_frame, anchor="nw")

        self.group_labels = {
            'R': tk.Label(self.group_frame, text="R: 00:00:00", font=("Helvetica", 14), fg="red"),
            'B': tk.Label(self.group_frame, text="B: 00:00:00", font=("Helvetica", 14), fg="blue"),
            'G': tk.Label(self.group_frame, text="G: 00:00:00", font=("Helvetica", 14), fg="green")
        }
        for lbl in self.group_labels.values():
            lbl.pack(side="left", padx=10)

        self.group_frame.bind("<Configure>", lambda e: self.group_canvas.configure(scrollregion=self.group_canvas.bbox("all")))

        self.start_button = tk.Button(root, text="START", command=self.start_timer)
        self.start_button.pack(pady=5)

        self.update_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.update_thread.start()

        self.app_group_map = {
            'chrome.exe': 'R',
            'msedge.exe': 'R',
            'zotero.exe': 'R',
            'winword.exe': 'B',
            'excel.exe': 'G',
            'code.exe': 'G',
        }

        self.group_times = {'R': 0, 'B': 0, 'G': 0}

    def start_timer(self):
        self.started = True
        self.last_check = time.time()
        self.start_button.config(state="disabled")
        self.status_label.config(text="木を成長させよう！", fg="gray")

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

            # 30秒ごとにリンゴ出現
            for group_key in ['R', 'G', 'B']:
                if self.group_times[group_key] >= 30:
                    if group_key not in [g for g, _ in self.apple_drops]:
                        unused = [p for p in self.apple_positions if p not in self.used_positions]
                        if unused:
                            pos = unused[0]  # random.choice(unused) に変更も可
                            self.apple_drops.append((group_key, pos))
                            self.used_positions.append(pos)

            self.update_label()
            self.update_group_labels()
            self.update_image()

    def update_group_labels(self):
        for group, seconds in self.group_times.items():
            hrs, rem = divmod(seconds, 3600)
            mins, secs = divmod(rem, 60)
            self.group_labels[group].config(text=f"{group}: {hrs:02}:{mins:02}:{secs:02}")

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
        for group, pos in self.apple_drops:
            apple = self.apple_images[group].copy()
            tree.alpha_composite(apple, dest=pos)

        tk_image = ImageTk.PhotoImage(tree)
        self.image_label.config(image=tk_image)
        self.image_label.image = tk_image

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenTimeApp(root)
    root.mainloop()