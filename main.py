# main.py (без изменений, кроме импортов)
import tkinter as tk
from gui.main_window import MainWindow
from utils.config import ConfigManager
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    root = tk.Tk()
    app = MainWindow(root)

    def on_closing():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()