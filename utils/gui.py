from tkinter import ttk
import tkinter as tk
from base64 import b64decode
from os import remove

class UI:
    def __init__(self):
        self.root = tk.Tk()

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

    def ui_init(self, icon_in_base_64, convert_file_callback, open_file_callback):
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

        ttk.Style().configure('std.TButton', font=('Helvetica', 10, 'bold'))
        ttk.Style().configure('cycle.TButton', font=('Helvetica', 6))
        ttk.Style().configure('cycle.TLabel', font=('Helvetica', 9), background='#d8d8d8')
        ttk.Style().configure('collide.TLabel', font=('Helvetica', 9))

        self.optimize, self.texturize, self.log = tk.IntVar(value=1), tk.IntVar(value=0), tk.IntVar(value=0)
        self.aesthetic_path, self.file_path, self.path_name = tk.StringVar(), '', ''
        self.player_cycle_name, self.camera_cycle_name = tk.StringVar(), tk.StringVar()
        self.player_cycle_name.set('Inherit'), self.camera_cycle_name.set('Inherit')
        self.input_lbl = ttk.Label(self.root, textvariable=self.aesthetic_path, background='#d8d8d8', width=26, anchor=tk.CENTER, font=('Helvetica', 9, 'italic'))
        self.input_btn = ttk.Button(self.root, text='Select triangulated .obj', width=25, style='std.TButton', command=open_file_callback)
        self.optimize_box = ttk.Checkbutton(self.root, text="Optimize object count", variable=self.optimize, onvalue=1, offvalue=0)
        self.texturize_box = ttk.Checkbutton(self.root, text="Texturize using .mtl file", variable=self.texturize, onvalue=1, offvalue=0)
        self.log_box = ttk.Checkbutton(self.root, text="Convert from directory", variable=self.log, onvalue=1, offvalue=0)

        self.player_collide_lbl = ttk.Label(self.root, text='Player collision', width=16, style='collide.TLabel')
        self.player_collision_cycle_lbtn = ttk.Button(self.root, text='◀', width=1, style='cycle.TButton', command=self.left_cycle_player)
        self.player_collision_cycle_lbl = ttk.Label(self.root, textvariable=self.player_cycle_name, width=7, anchor=tk.CENTER, style='cycle.TLabel')
        self.player_collision_cycle_rbtn = ttk.Button(self.root, text='▶', width=1, style='cycle.TButton', command=self.right_cycle_player)

        self.camera_collide_lbl = ttk.Label(self.root, text='Camera collision', width=15, style='collide.TLabel')
        self.camera_collision_cycle_lbtn = ttk.Button(self.root, text='◀', width=1, style='cycle.TButton', command=self.left_cycle_camera)
        self.camera_collision_cycle_lbl = ttk.Label(self.root, textvariable=self.camera_cycle_name, width=7, anchor=tk.CENTER, style='cycle.TLabel')
        self.camera_collision_cycle_rbtn = ttk.Button(self.root, text='▶', width=1, style='cycle.TButton', command=self.right_cycle_camera)

        self.convert_btn = ttk.Button(self.root, text='Convert', width=25, style='std.TButton', command=convert_file_callback)

    def buttonize(self):
        self.root.geometry('185x180')  # set window geometry
        self.progress_bar['value'] = 0  # set progress bar to empty
        self.input_lbl.place(x=0, y=0)  # place labels and buttons
        self.input_btn.place(x=0, y=19)
        self.optimize_box.place(x=3, y=47)
        self.texturize_box.place(x=3, y=67)
        self.log_box.place(x=3, y=87)
        self.player_collide_lbl.place(x=11, y=110)
        self.player_collision_cycle_lbtn.place(x=100, y=110)
        self.player_collision_cycle_lbl.place(x=115, y=110)
        self.player_collision_cycle_rbtn.place(x=170, y=110)
        self.camera_collide_lbl.place(x=0, y=130)
        self.camera_collision_cycle_lbtn.place(x=100, y=130)
        self.camera_collision_cycle_lbl.place(x=115, y=131)
        self.camera_collision_cycle_rbtn.place(x=170, y=130)
        self.convert_btn.place(x=0, y=154)

    def set_wrapping_up(self):
        self.progress_bar.place_forget()
        self.progress_lbl.place_forget()
        self.progress_uuid.place_forget()
        self.root.update()
        self.root.geometry('60x21')
        self.lbl = ttk.Label(self.root, text='wrapping up...', font=('Helvetica', 10, 'bold italic'))
        self.lbl.place(x=0, y=0)
        self.root.update()

