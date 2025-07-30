import tkinter as tk
import time
import threading

class ScreenTimeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("スクリーンタイム計測")

        self.time_elapsed = 0  # 秒数
        self.running = False
        self.last_check = time.time()

        self.label = tk.Label(root, text="00:00:00", font=("Helvetica", 32))
        self.label.pack(pady=20)

        self.start_button = tk.Button(root, text="スタート", command=self.start_timer)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(root, text="ストップ", command=self.stop_timer, state="disabled")
        self.stop_button.pack(pady=5)

        # タイマー更新スレッド開始
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
            if self.running:
                now = time.time()
                self.time_elapsed += int(now - self.last_check)
                self.last_check = time.time()
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
