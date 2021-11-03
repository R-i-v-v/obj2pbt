from tkinter import ttk
import tkinter as tk
from base64 import b64decode
from os import remove

class UI:
    def __init__(self):
        self.root = tk.Tk()

    def ui_init(self, icon_in_base_64, convert_file_callback, open_file_callback):
        print(self)
        self.root.title('obj2pbt')  # set window title
        self.root.resizable(width=False, height=False)  # prevent resizing
        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=230, mode='determinate', value=0)


        icon_data = b64decode(icon_in_base_64)
        temp_icon_file = 'temp_icon.ico'
        icon_file = open(temp_icon_file, 'wb')
        icon_file.write(icon_data)
        icon_file.close()
        self.root.wm_iconbitmap(temp_icon_file)
        remove(temp_icon_file)

        self.optimize, self.texturize, self.log = tk.IntVar(value=1), tk.IntVar(value=0), tk.IntVar(value=0)
        self.aesthetic_path, self.file_path, self.path_name = tk.StringVar(), '', ''
        self.input_style = ttk.Style()
        self.input_style.configure('TButton', font=('Helvetica', 10, 'bold'))
        self.input_lbl = ttk.Label(self.root, textvariable=self.aesthetic_path, background='#d8d8d8', width=23, anchor=tk.CENTER, font=('Helvetica', 9, 'italic'))
        self.input_btn = ttk.Button(self.root, text='Select triangulated .obj', width=22, style='TButton', command=open_file_callback)
        self.optimize_box = ttk.Checkbutton(self.root, text="Optimize object count", variable=self.optimize, onvalue=1, offvalue=0)
        self.texturize_box = ttk.Checkbutton(self.root, text="Texturize using .mtl file", variable=self.texturize, onvalue=1, offvalue=0)
        self.log_box = ttk.Checkbutton(self.root, text="Log from directory", variable=self.log, onvalue=1, offvalue=0)
        self.convert_btn = ttk.Button(self.root, text='Convert', width=22, style='TButton', command=convert_file_callback)

    def buttonize(self):
        self.root.geometry('164x141')  # set window geometry
        self.progress_bar['value'] = 0  # set progress bar to empty
        self.input_lbl.place(x=0, y=0)  # place labels and buttons
        self.input_btn.place(x=0, y=19)
        self.optimize_box.place(x=3, y=50)
        self.texturize_box.place(x=3, y=70)
        self.log_box.place(x=3, y=90)
        self.convert_btn.place(x=0, y=115)

    def set_wrapping_up(self):
        self.progress_bar.place_forget()
        self.progress_lbl.place_forget()
        self.progress_uuid.place_forget()
        self.root.update()
        self.root.geometry('60x21')
        self.lbl = ttk.Label(self.root, text='wrapping up...', font=('Helvetica', 10, 'bold italic'))
        self.lbl.place(x=0, y=0)
        self.root.update()

