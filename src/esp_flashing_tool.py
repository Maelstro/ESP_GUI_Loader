import tkinter as tk
from window import MainWindow
import sys

if __name__ == '__main__':
    root = tk.Tk()
    app = MainWindow(root)
    sys.stdout.write = app.redirector
    sys.stderr.write = app.redirector
    root.mainloop()