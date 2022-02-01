from tkinter import ttk
import tkinter as tk
from base64 import b64decode
from os import remove

class UI:
    def __init__(self):
        self.root = tk.Tk()
        self.__version__ = 0.0

    def version(self, number: float):
        self.__version__ = number

    def setting(self):
        player = 'inheritfromparent' if self.player_cycle_name.get() == 'Inherit' else 'forceon' if self.player_cycle_name.get() == 'Force On' else 'forceoff'
        camera = 'inheritfromparent' if self.camera_cycle_name.get() == 'Inherit' else 'forceon' if self.camera_cycle_name.get() == 'Force On' else 'forceoff'
        return (player, camera)

    def cycle(self, method: str, input: tk.StringVar):
        if method == 'left':
            if input.get() == 'Inherit':
                input.set('Force On')
            elif input.get() == 'Force On':
                input.set('Force Off')
            elif input.get() == 'Force Off':
                input.set('Inherit')
        elif method == 'right':
            if input.get() == 'Inherit':
                input.set('Force Off')
            elif input.get() == 'Force On':
                input.set('Inherit')
            elif input.get() == 'Force Off':
                input.set('Force On')

    def left_cycle_player(self):
        self.cycle('left', self.player_cycle_name)

    def right_cycle_player(self):
        self.cycle('right', self.player_cycle_name)

    def left_cycle_camera(self):
        self.cycle('left', self.camera_cycle_name)

    def right_cycle_camera(self):
        self.cycle('right', self.camera_cycle_name)

    def logbox(self):
        if self.log.get() == 1:
            self.obj_button_text.set("Select directory of .obj's")
        else:
            self.obj_button_text.set('Select triangulated .obj')
        self.aesthetic_path.set('')
        self.file_path, self.path_name = '', ''

    def ui_init(self, icon_in_base_64, convert_file_callback, open_file_callback):
        self.root.title(f'obj2pbt v{str(self.__version__)}')  # set window title
        self.root.resizable(width=False, height=False)  # prevent resizing
        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=230, mode='determinate', value=0)

        icon_data = b64decode(icon_in_base_64)
        temp_icon_file = 'temp_icon.ico'
        icon_file = open(temp_icon_file, 'wb')
        icon_file.write(icon_data)
        icon_file.close()
        self.root.wm_iconbitmap(temp_icon_file)
        remove(temp_icon_file)

        ttk.Style().configure('std.TButton', font=('Helvetica', 10, 'bold'))
        ttk.Style().configure('cycle.TButton', font=('Helvetica', 6))
        ttk.Style().configure('cycle.TLabel', font=('Helvetica', 9), background='#d8d8d8')
        ttk.Style().configure('collide.TLabel', font=('Helvetica', 9))
        ttk.Style().configure('version.TLabel', font=('Helvetica', 7, 'italic'), background='#d8d8d8')

        self.optimize, self.texturize, self.log = tk.IntVar(value=1), tk.IntVar(value=0), tk.IntVar(value=0)
        self.aesthetic_path, self.file_path, self.path_name, self.modelize = tk.StringVar(), '', '', tk.IntVar(value=0)
        self.player_cycle_name, self.camera_cycle_name = tk.StringVar(value='Inherit'), tk.StringVar(value='Inherit')
        self.separator = ttk.Separator(self.root, orient='horizontal')
        self.obj_button_text = tk.StringVar(value='Select triangulated .obj')
        self.input_lbl = ttk.Label(self.root, textvariable=self.aesthetic_path, background='#d8d8d8', width=26, anchor=tk.CENTER, font=('Helvetica', 9, 'italic'))
        self.input_btn = ttk.Button(self.root, textvariable=self.obj_button_text, width=25, style='std.TButton', command=open_file_callback)
        self.log_box = ttk.Checkbutton(self.root, text="Convert from directory", variable=self.log, onvalue=1, offvalue=0, command=self.logbox)
        self.optimize_box = ttk.Checkbutton(self.root, text="Optimize object count", variable=self.optimize, onvalue=1, offvalue=0)
        self.texturize_box = ttk.Checkbutton(self.root, text="Texturize using .mtl file", variable=self.texturize, onvalue=1, offvalue=0)
        self.merged_model_box = ttk.Checkbutton(self.root, text="Use merged models (beta)", variable=self.modelize, onvalue=1, offvalue=0)

        self.player_collide_lbl = ttk.Label(self.root, text='Player collision', width=16, style='collide.TLabel')
        self.player_collision_cycle_lbtn = ttk.Button(self.root, text='◀', width=1, style='cycle.TButton', command=self.left_cycle_player)
        self.player_collision_cycle_lbl = ttk.Label(self.root, textvariable=self.player_cycle_name, width=7, anchor=tk.CENTER, style='cycle.TLabel')
        self.player_collision_cycle_rbtn = ttk.Button(self.root, text='▶', width=1, style='cycle.TButton', command=self.right_cycle_player)

        self.camera_collide_lbl = ttk.Label(self.root, text='Camera collision', width=15, style='collide.TLabel')
        self.camera_collision_cycle_lbtn = ttk.Button(self.root, text='◀', width=1, style='cycle.TButton', command=self.left_cycle_camera)
        self.camera_collision_cycle_lbl = ttk.Label(self.root, textvariable=self.camera_cycle_name, width=7, anchor=tk.CENTER, style='cycle.TLabel')
        self.camera_collision_cycle_rbtn = ttk.Button(self.root, text='▶', width=1, style='cycle.TButton', command=self.right_cycle_camera)

        self.convert_btn = ttk.Button(self.root, text='Convert', width=25, style='std.TButton', command=convert_file_callback)
        self.version_lbl = ttk.Label(self.root, text=f'obj2pbt v{self.__version__}', width=12, style='version.TLabel')

    def buttonize(self):
        self.root.geometry('185x200')  # set window geometry
        self.progress_bar['value'] = 0  # set progress bar to empty
        self.input_lbl.place(x=0, y=0)  # place labels and buttons
        self.input_btn.place(x=0, y=19)
        self.log_box.place(x=20, y=44)
        self.separator.place(x=0, y=65, relwidth=1.0)
        self.optimize_box.place(x=3, y=67)
        self.texturize_box.place(x=3, y=87)
        self.merged_model_box.place(x=3, y=107)
        self.player_collide_lbl.place(x=11, y=130)
        self.player_collision_cycle_lbtn.place(x=100, y=130)
        self.player_collision_cycle_lbl.place(x=115, y=130)
        self.player_collision_cycle_rbtn.place(x=170, y=130)
        self.camera_collide_lbl.place(x=0, y=150)
        self.camera_collision_cycle_lbtn.place(x=100, y=150)
        self.camera_collision_cycle_lbl.place(x=115, y=151)
        self.camera_collision_cycle_rbtn.place(x=170, y=150)
        self.convert_btn.place(x=0, y=174)
        self.version_lbl.place(x=3, y=3)
        
    def unplace(self):
        self.input_btn.place_forget()
        self.input_lbl.place_forget()
        self.convert_btn.place_forget()
        self.log_box.place_forget()
        self.separator.place_forget()
        self.optimize_box.place_forget()
        self.texturize_box.place_forget()
        self.merged_model_box.place_forget()
        self.player_collide_lbl.place_forget()
        self.player_collision_cycle_lbl.place_forget()
        self.player_collision_cycle_lbtn.place_forget()
        self.player_collision_cycle_rbtn.place_forget()
        self.camera_collide_lbl.place_forget()
        self.camera_collision_cycle_lbl.place_forget()
        self.camera_collision_cycle_lbtn.place_forget()
        self.camera_collision_cycle_rbtn.place_forget()

    def set_wrapping_up(self, uuid, entry):
        self.progress_bar.place_forget()
        self.progress_lbl.place_forget()
        self.progress_uuid.place_forget()
        self.root.update()
        self.root.geometry('130x61')
        self.lbl = ttk.Label(self.root, text=f'wrapping up...', font=('Helvetica', 10, 'bold italic'))
        self.lbl.place(x=0, y=0)
        self.separator.place(x=0, y=23, relwidth=1.0)
        self.name_lbl = ttk.Label(self.root, text=f'{entry}.pbt', font=('Helvetica', 8))
        self.name_lbl.place(x=0, y=25)
        self.uuid_lbl = ttk.Label(self.root, text=f'UUID: {uuid}', font=('Helvetica', 8))
        self.uuid_lbl.place(x=0, y=40)
        self.root.update()

