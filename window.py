import tkinter as tk
from tkinter import filedialog

class MainWindow(tk.Tk):
    def __init__(self, master):
        self.root = master
        self.root.title("ESP32 GUI Flasher")
        self.main_text = tk.Label(self.root, text="ESP32 GUI Flasher")
        self.main_text.pack()

        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_path)
        self.browse_button.pack()

        self.flash_button = tk.Button(self.root, text="Flash", command=self.flash_program)
        self.flash_button.pack()

        self.text_field = tk.Text(self.root, height=50, width=150)
        self.text_field.pack()

    def browse_path(self):
        self.directory = filedialog.askdirectory()

    def show_text(self, text):
        self.text_field.insert(tk.END, text)
        self.text_field.see(tk.END)
        self.text_field.update_idletasks()

    def flash_program(self):
        # self.show_text(self.directory)
        

