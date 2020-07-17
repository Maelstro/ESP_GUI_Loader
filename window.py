import tkinter as tk
from tkinter import filedialog
from subprocess import Popen, PIPE
import serial.tools.list_ports
import threading

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

        # Project path browser button
        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_path)
        self.browse_button.pack()

        # Flashing button
        self.flash_button = tk.Button(self.root, text="Flash", command=self._flash_wrapper)
        self.flash_button.pack()

        self.text_field = tk.Text(self.root, height=40, width=120)
        self.text_field.pack()

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

    def browse_path(self):
        self.project_directory = filedialog.askdirectory()

    def show_text(self, text):
        self.text_field.insert(tk.END, text)
        self.text_field.see(tk.END)
        self.text_field.update_idletasks()


    def flash_program(self):
        # Detect the COM port
        try:
            self.autodetect_com_port()
        except self.selected_port == "":
            print("Did not detect any ESP32!")
        finally:
            print(self.selected_port)
            _cmd_flash = "idf.py -p " + self.selected_port + " flash"
            print(_cmd_flash)
            # TODO: Add dynamic selection of ESP toolchain
            # Currently - hardcoded path to ESP-IDF toolchain
            self.append_command("C:")
            self.append_command("C:\\ESP\\esp-idf\\export.bat")

            if self.project_directory == "":
                print("Brak ustawionej ścieżki do projektu!")

            else:
                self.project_directory = self.project_directory.replace("/", "\\")
                _prefix = self.project_directory[:2]
                self.append_command(_prefix)
                self.append_command("cd " + self.project_directory)
                self.append_command("idf.py fullclean & idf.py build")
                self.append_command(_cmd_flash)

                print("Command: {}".format(self.flash_command))

                process = Popen(self.flash_command,
                                bufsize=4096,
                                stdout=PIPE,
                                stderr=PIPE,
                                shell=True)

                for line in process.stdout:
                    self.show_text(line)

            # Clear command
            self.flash_command = ""
            self.flash_button.config(state=tk.ACTIVE)

    def _flash_wrapper(self):
        # Create thread with flashing method
        self.flash_button.config(state=tk.DISABLED)
        threading.Thread(target=self.flash_program).start()


