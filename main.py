import tkinter as tk

from gui.main_window import MainWindow


def main():
    root = tk.Tk()
    MainWindow(root)

    def on_closing():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
