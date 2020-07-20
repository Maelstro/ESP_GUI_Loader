import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from subprocess import Popen, PIPE
import serial.tools.list_ports
import threading
import os

class MainWindow(tk.Tk):
    def __init__(self, master):
        # Variables
        self.flash_command = ""
        self.project_directory = ""
        self.esp_tools_path = ""
        self.selected_port = ""

        self.root = master
        self.root.geometry("600x450+650+150")
        self.root.minsize(120, 1)
        self.root.maxsize(1924, 1061)
        self.root.resizable(1, 1)
        self.root.title("ESP32 GUI Flashing Tool")

        self.main_text = tk.Label(self.root, text="ESP32 GUI Flasher")
        self.main_text.pack()

        self.label_esp_path = tk.Label(self.root, text="ESP-IDF Tools path")
        self.label_esp_path.place(relx=0.033, rely=0.022)

        self.text_esp_path = tk.Text(self.root)
        self.text_esp_path.place(relx=0.033, rely=0.067, relheight=0.053, relwidth=0.357)
        self.text_esp_path.config(wrap='none')

        self.text_field = tk.Text(self.root)
        self.text_field.place(relx=0.033, rely=0.4, relheight=0.564, relwidth=0.933)

        self.label_proj_dir = tk.Label(self.root, text="Project directory")
        self.label_proj_dir.place(relx=0.033, rely=0.156)

        self.text_proj_dir = tk.Text(self.root)
        self.text_proj_dir.place(relx=0.033, rely=0.2, relheight=0.053, relwidth=0.357)
        self.text_proj_dir.config(wrap='none')

        self.button_esp_browse = tk.Button(self.root, text="Browse ESP-IDF Tools",
                                           command=lambda: self.browse_path("esp_idf"))
        self.button_esp_browse.place(relx=0.4, rely=0.067, height=24, width=127)

        self.button_proj_browse = tk.Button(self.root, text="Browse project",
                                            command=lambda: self.browse_path("project"))
        self.button_proj_browse.place(relx=0.4, rely=0.2, height=24, width=127)

        self.button_flash = tk.Button(self.root, text="Flash program", command=self._flash_wrapper)
        self.button_flash.place(relx=0.65, rely=0.067, height=84, width=157)

    def append_command(self, cmd: str):
        if len(self.flash_command) < 1:
            self.flash_command += cmd
        else:
            self.flash_command += (" && " + cmd)

    def autodetect_com_port(self):
        device_list = serial.tools.list_ports.comports()
        for device in device_list:
            if "CP210x" in device[1]:
                self.selected_port = device[0]
                break

    def browse_path(self, type: str):
        if type == "project":
            self.project_directory = filedialog.askdirectory()
            self.text_proj_dir.insert(tk.END, self.project_directory)
            self.text_proj_dir.see(tk.END)
        elif type == "esp_idf":
            self.esp_tools_path = filedialog.askdirectory()
            self.text_esp_path.insert(tk.END, self.esp_tools_path)
            self.text_esp_path.see(tk.END)


    def show_text(self, text):
        self.text_field.insert(tk.END, text)
        self.text_field.see(tk.END)
        self.text_field.update_idletasks()

    def show_messagebox(self, title: str, msg: str):
        messagebox.showwarning(title=title, message=msg)
        print(msg)

    def flash_program(self):
        # Detect the COM port
        self.autodetect_com_port()

        if self.selected_port == "":
            msg = "Did not detect any ESP32!"
            self.show_messagebox("No ESP32 detected", msg)
        else:
            print(self.selected_port)
            _cmd_flash = "idf.py -p " + self.selected_port + " flash"
            print(_cmd_flash)

            if self.esp_tools_path == "":
                msg = "ESP-IDF Tools path is not set!"
                self.show_messagebox("No ESP-IDF Tools set", msg)
            elif "export.bat" not in os.listdir(self.esp_tools_path):
                msg = "Export.bat not found, wrong ESP-IDF Tools directory!"
                self.show_messagebox("Wrong ESP-IDF Tools directory", msg)
            else:
                self.esp_tools_path = self.esp_tools_path.replace("/", "\\")
                _prefix = self.esp_tools_path[:2]
                self.append_command(_prefix)
                self.append_command(self.esp_tools_path + "\\export.bat")

                if self.project_directory == "":
                    msg = "Project directory is not set!"
                    self.show_messagebox("Project directory not set", msg)

                else:
                    self.project_directory = self.project_directory.replace("/", "\\")
                    _prefix = self.project_directory[:2]
                    self.append_command(_prefix)
                    self.append_command("cd " + self.project_directory)
                    self.append_command("idf.py fullclean && idf.py build")
                    self.append_command(_cmd_flash)

                    print("Command: {}".format(self.flash_command))

                    process = Popen(self.flash_command,
                                    bufsize=4096,
                                    stdout=PIPE,
                                    stderr=PIPE,
                                    shell=True)

                    for line in process.stdout:
                        self.show_text(line)

                    streamdata = process.communicate()[0]
                    rc = process.returncode
                    print("Return code: {}".format(rc))

                    if rc == 2:
                        msg = "Error during flashing the program to the microcontroller. esptool.py not installed on " \
                              "this Python version or wrong user permissions (must be 'Run as Administrator'). "
                        messagebox.showerror(title='Error during flashing', message=msg)
                    elif rc == 0:
                        msg = "Program flashed correctly to the microcontroller."
                        messagebox.showinfo(title="Finished without errors", message=msg)

        # Clear command
        self.flash_command = ""
        self.button_flash.config(state=tk.ACTIVE)

    def _flash_wrapper(self):
        # Create thread with flashing method
        self.button_flash.config(state=tk.DISABLED)
        threading.Thread(target=self.flash_program).start()




