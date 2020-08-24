import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import serial.tools.list_ports
import threading
import esptool

class MainWindow(tk.Tk):
    def __init__(self, master):
        # Variables
        self.project_directory = ""
        self.selected_port = ""

        self.root = master
        self.root.geometry("600x450+650+150")
        self.root.minsize(120, 1)
        self.root.maxsize(1924, 1061)
        self.root.resizable(1, 1)
        self.root.title("ESP32 GUI Flashing Tool")

        self.main_text = tk.Label(self.root, text="ESP32 GUI Flasher")
        self.main_text.pack()

        self.text_field = tk.Text(self.root)
        self.text_field.place(relx=0.033, rely=0.4, relheight=0.564, relwidth=0.933)

        self.label_proj_dir = tk.Label(self.root, text="Project directory")
        self.label_proj_dir.place(relx=0.033, rely=0.022)

        self.text_proj_dir = tk.Text(self.root)
        self.text_proj_dir.place(relx=0.033, rely=0.067, relheight=0.053, relwidth=0.357)
        self.text_proj_dir.config(wrap='none')

        self.label_com_port = tk.Label(self.root, text="COM port with ESP32")
        self.label_com_port.place(relx=0.033, rely=0.156)

        self.text_com_port = tk.Text(self.root)
        self.text_com_port.place(relx=0.033, rely=0.2, relheight=0.053, relwidth=0.357)
        self.text_com_port.config(wrap='none')

        self.button_proj_browse = tk.Button(self.root, text="Browse project",
                                            command=lambda: self.browse_project_path())
        self.button_proj_browse.place(relx=0.4, rely=0.067, height=24, width=127)

        self.button_detect_port = tk.Button(self.root, text="Detect ESP32",
                                            command=lambda: self.autodetect_com_port())
        self.button_detect_port.place(relx=0.4, rely=0.2, height=24, width=127)

        self.button_flash = tk.Button(self.root, text="Flash program", command=self._flash_wrapper)
        self.button_flash.place(relx=0.65, rely=0.067, height=84, width=157)
        self.button_flash.config(state=tk.DISABLED)

    def redirector(self, input_str):
        self.text_field.insert(tk.INSERT, input_str)
        self.text_field.see(tk.END)

    def autodetect_com_port(self):
        device_list = serial.tools.list_ports.comports()
        for device in device_list:
            if "CP210x" in device[1]:
                self.selected_port = device[0]
                self.text_com_port.delete("1.0", tk.END)
                self.text_com_port.insert(tk.END, self.selected_port)
                self.text_com_port.see(tk.END)
                self.button_flash.config(state=tk.ACTIVE)
                break
        if self.selected_port == "":
            msg = "Did not detect any ESP32!"
            self.show_messagebox("No ESP32 detected", msg)


    def browse_project_path(self):
        self.project_directory = filedialog.askdirectory()
        self.text_proj_dir.delete("1.0", tk.END)
        self.text_proj_dir.insert(tk.END, self.project_directory)
        self.text_proj_dir.see(tk.END)

    def show_text(self, text):
        self.text_field.insert(tk.END, text)
        self.text_field.see(tk.END)
        self.text_field.update_idletasks()

    def show_messagebox(self, title: str, msg: str):
        messagebox.showwarning(title=title, message=msg)
        print(msg)

    def flash_program(self):
        self.button_flash.config(state=tk.DISABLED)
        flash_command = []
        flash_command.extend(['--baud', '460800', '--port', self.selected_port, 'write_flash'])
        try:
            with open(self.project_directory + '/flash_project_args') as f:
                args = []
                lines = f.read().split('\n')
                for i, line in enumerate(lines):
                    split_line = line.split(' ')
                    if 0 < i < len(lines) - 1:
                        split_line[1] = self.project_directory + '/' + split_line[1]
                        args.extend(split_line)
            flash_command.extend(args)
            esptool.main(flash_command)
        except FileNotFoundError:
            msg = ("No flash_project_args found! "
                   "Change the project directory for the one that has flash_project_args in it.")
            self.show_messagebox("No flash_project_args found", msg)
        # Clear command
        self.button_flash.config(state=tk.ACTIVE)

    def _flash_wrapper(self):
        # Create thread with flashing method
        self.button_flash.config(state=tk.DISABLED)
        threading.Thread(target=self.flash_program).start()




