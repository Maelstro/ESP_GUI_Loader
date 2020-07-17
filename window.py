import tkinter as tk
from tkinter import filedialog
from subprocess import Popen, PIPE

class MainWindow(tk.Tk):
    def __init__(self, master):
        # Variables
        self.flash_command = ""
        self.project_directory = ""
        self.selected_port = ""

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

    def set_command(self, cmd: str):
        if len(self.flash_command) < 1:
            self.flash_command += cmd
        else:
            self.flash_command += (" & " + cmd)

    def browse_path(self):
        self.project_directory = filedialog.askdirectory()

    def show_text(self, text):
        self.text_field.insert(tk.END, text)
        self.text_field.see(tk.END)
        self.text_field.update_idletasks()

    def flash_program(self):
        # TODO: Add flashing program to ESP32 (Win10)
        # Currently - hardcoded
        self.set_command("C:")
        self.set_command("C:\\ESP\\esp-idf\\export.bat")
        self.set_command("F:")
        self.set_command("cd F:\\annda_esp32\\micro\\tools\\make\\gen\\esp_xtensa-esp32\\prj\\annda_esp32\\esp-idf")
        self.set_command("idf.py fullclean")
        self.set_command("idf.py build")

        process = Popen(self.flash_command,
                        bufsize=4096,
                        stdout=PIPE,
                        stderr=PIPE,
                        shell=True)

        for line in process.stdout:
            self.show_text(line)

        err_line = ""
        for line in process.stderr:
            err_line += line

        print(err_line == "")

        # Clear command
        self.flash_command = ""


