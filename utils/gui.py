from tkinter import ttk
import tkinter as tk
from base64 import b64decode
import asyncio
from time import sleep
from os import remove
from .elements import start_progress, end_progress, load_progress, version_four, logo_image
from PIL import Image, ImageTk, ImageSequence
from pyglet import font
import threading

class UI:
    def __init__(self):
        self.temp_logo_file, self.temp_version_file, self.logo_image, self.version_image = None, None, None, None
        self.some_flag, self.central_frame, self.logo_img, self.version_img = True, None, None, None
        self.animated_gif, self.start_prog, self.end_prog, self.load_lbl, self.border = None, None, None, None, None
        self.uuid_lbl, self.name_lbl, self.lbl, self.progress_uuid, self.progress_lbl = None, None, None, None, None
        self.version_lbl, self.convert_btn, self.camera_collision_cycle_lbtn, self.temp_load = None, None, None, None
        self.camera_collision_cycle_rbtn, self.camera_collision_cycle_lbl, self.camera_collide_lbl = None, None, None
        self.player_collision_cycle_rbtn, self.player_collision_cycle_lbl, self.log_box = None, None, None
        self.player_collision_cycle_lbtn, self.player_collide_lbl, self.merged_model_box = None, None, None
        self.texturize_box, self.optimize_box, self.input_btn, self.input_lbl = None, None, None, None
        self.prog_load_frames, self.prog_end, self.temp_end, self.prog_start, self.canvas = None, None, None, None, None
        self.log, self.optimize, self.path_name, self.file_path, self.temp_start = None, None, None, None, None
        self.texturize, self.modelize, self.aesthetic_path, self.obj_button_text = None, None, None, None
        self.separator, self.progress_bar, self.camera_cycle_name, self.player_cycle_name = None, None, None, None
        self.root = tk.Tk()
        self.__version__ = 0.0

    def initialize_colors(self):
        custom_style = ttk.Style()
        font.add_file('montserrat.ttf')
        self.root.call('source', 'theme.tcl')
        custom_style.theme_use('obj2pbt')
        custom_style.configure('TButton', background='#0E0E0E', foreground='#0E0E0E', width=20, borderwidth=1,
                               focusthickness=3, focuscolor='none')
        ttk.Style().configure('std.TButton', font=('montserrat', 12, 'bold'))
        ttk.Style().configure('cycle.TButton', font=('Helvetica', 12, 'bold'))
        ttk.Style().configure('cycle.TLabel', font=('montserrat', 9), background='#0E0E0E')
        ttk.Style().configure('collide.TLabel', font=('montserrat', 9))
        ttk.Style().configure('version.TLabel', font=('montserrat', 10), background='white', foreground='black')
        ttk.Style().configure('TLabelframe', labelmargins=(0, -4, 25, 13))
        ttk.Style().configure('TLabelframe.Label', font=('montserrat', 9, 'bold'), background='#0E0E0E', foreground='#FF392B')

    def version(self, number: float):
        self.__version__ = number

    def setting(self):
        player = 'inheritfromparent' if self.player_cycle_name.get() == 'Inherit' else 'forceon' if self.player_cycle_name.get() == 'Force On' else 'forceoff'
        camera = 'inheritfromparent' if self.camera_cycle_name.get() == 'Inherit' else 'forceon' if self.camera_cycle_name.get() == 'Force On' else 'forceoff'
        return player, camera

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

    def change_model(self):
        if self.modelize.get() == 1:
            self.merged_model_box.state(['alternate'])

    def ui_init(self, icon_in_base_64, convert_file_callback, open_file_callback):
        self.root.title(f'obj2pbt v{str(self.__version__)}')  # set window title
        self.root.resizable(width=False, height=False)  # prevent resizing
        self.progress_bar = ttk.Progressbar(self.root, orient='horizontal', length=370, mode='determinate', value=0)
        icon_data, logo_data, version_data = b64decode(icon_in_base_64), b64decode(logo_image), b64decode(version_four)
        temp_icon_file, self.temp_logo_file, self.temp_version_file = 'temp_icon.ico', 'temp_logo.png', 'temp_version.png'
        icon_file, logo_file, version_file = open(temp_icon_file, 'wb'), open(self.temp_logo_file, 'wb'), open(self.temp_version_file, 'wb')
        icon_file.write(icon_data), logo_file.write(logo_data), version_file.write(version_data)
        icon_file.close(), logo_file.close(), version_file.close()
        self.version_img, self.logo_img = ImageTk.PhotoImage(file=self.temp_version_file), ImageTk.PhotoImage(file=self.temp_logo_file)
        self.root.wm_iconbitmap(temp_icon_file)
        # self.root.wm_attributes('-alpha', 0.5)
        remove(temp_icon_file)
        self.initialize_colors()

        self.optimize, self.texturize, self.log = tk.IntVar(value=1), tk.IntVar(value=0), tk.IntVar(value=0)
        self.aesthetic_path, self.file_path, self.path_name, self.modelize = tk.StringVar(), '', '', tk.IntVar(value=0)
        self.player_cycle_name, self.camera_cycle_name = tk.StringVar(value='Inherit'), tk.StringVar(value='Inherit')
        # self.canvas = tk.Canvas()
        self.central_frame = ttk.Labelframe(self.root, labelanchor='se', text=f'   obj2pbt v{self.__version__}   ',
                                            width=315, height=363, style='TLabelframe')
        self.separator = ttk.Separator(self.central_frame, orient='horizontal')
        self.obj_button_text = tk.StringVar(value='Select triangulated .obj')
        self.input_lbl = ttk.Label(self.central_frame, textvariable=self.aesthetic_path, background='WHITE', width=20,
                                   anchor=tk.W, font=('montserrat', 14, 'bold'), foreground='BLACK')
        self.logo_image = ttk.Label(self.central_frame, borderwidth=0, image=self.logo_img)
        self.input_btn = ttk.Button(self.central_frame, textvariable=self.obj_button_text, width=23, style='std.TButton', command=open_file_callback)
        self.log_box = ttk.Checkbutton(self.central_frame, text="Convert from directory", variable=self.log, onvalue=1, offvalue=0, command=self.logbox)
        self.optimize_box = ttk.Checkbutton(self.central_frame, text="Optimize object count", variable=self.optimize, onvalue=1, offvalue=0)
        self.texturize_box = ttk.Checkbutton(self.central_frame, text="Texturize using .mtl file", variable=self.texturize, onvalue=1, offvalue=0)
        self.merged_model_box = ttk.Checkbutton(self.central_frame, text="Use merged models (beta)", variable=self.modelize, command=self.change_model)

        self.player_collide_lbl = ttk.Label(self.central_frame, text='Player collision', width=16, style='collide.TLabel')
        self.player_collision_cycle_lbtn = ttk.Button(self.central_frame, text='◀', width=1, style='cycle.TButton', command=self.left_cycle_player)
        self.player_collision_cycle_lbl = ttk.Label(self.central_frame, textvariable=self.player_cycle_name, width=7, anchor=tk.CENTER, style='cycle.TLabel')
        self.player_collision_cycle_rbtn = ttk.Button(self.central_frame, text='▶', width=1, style='cycle.TButton', command=self.right_cycle_player)

        self.camera_collide_lbl = ttk.Label(self.central_frame, text='Camera collision', width=15, style='collide.TLabel')
        self.camera_collision_cycle_lbtn = ttk.Button(self.central_frame, text='◀', width=1, style='cycle.TButton', command=self.left_cycle_camera)
        self.camera_collision_cycle_lbl = ttk.Label(self.central_frame, textvariable=self.camera_cycle_name, width=7, anchor=tk.CENTER, style='cycle.TLabel')
        self.camera_collision_cycle_rbtn = ttk.Button(self.central_frame, text='▶', width=1, style='cycle.TButton', command=self.right_cycle_camera)

        self.convert_btn = ttk.Button(self.central_frame, text='Convert', width=23, style='std.TButton', command=convert_file_callback)
        # self.version_lbl = ttk.Label(self.root, text=f'obj2pbt v{self.__version__}', width=12, style='version.TLabel')

    def buttonize(self):
        self.root.geometry('315x350')  # set window geometry
        self.progress_bar['value'] = 0  # set progress bar to empty
        self.central_frame.configure(width=315, height=363)
        self.central_frame.place(x=0, y=0)
        self.logo_image.place(x=10, y=10)
        self.input_lbl.place(x=25, y=22)  # place labels and buttons
        self.input_btn.place(x=25, y=57)
        self.log_box.place(x=40, y=92)
        self.separator.place(x=10, y=124, relwidth=0.935)
        self.optimize_box.place(x=25, y=132)
        self.texturize_box.place(x=25, y=159)
        self.merged_model_box.place(x=25, y=186)
        self.player_collide_lbl.place(x=37, y=223)
        self.player_collision_cycle_lbtn.place(x=165, y=222)
        self.player_collision_cycle_lbl.place(x=188, y=223)
        self.player_collision_cycle_rbtn.place(x=265, y=222)
        self.camera_collide_lbl.place(x=25, y=256)
        self.camera_collision_cycle_lbtn.place(x=165, y=255)
        self.camera_collision_cycle_lbl.place(x=188, y=256)
        self.camera_collision_cycle_rbtn.place(x=265, y=255)
        self.convert_btn.place(x=25, y=295)

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
        self.central_frame.place_forget()

    async def play_gif(self):
        global img
        if self.some_flag:
            img = Image.open(self.temp_load)
            self.load_lbl = ttk.Label(self.root, borderwidth=0)
            self.load_lbl.place(x=10, y=7)
            for img in ImageSequence.Iterator(img):
                img = img.resize((150, 150))
                img = ImageTk.PhotoImage(img)
                self.load_lbl.configure(image=img)
                self.root.update()
                await asyncio.sleep(0.02)
            # self.root.after(0, await self.play_gif())
        else:
            img = Image.open(self.temp_load)
            img.close()
            remove(self.temp_load)

    async def make_progress(self, uuid, entry_name):
        self.unplace()
        self.root.deiconify()
        self.root.geometry('600x170')
        self.some_flag = True
        start, end, load = b64decode(start_progress), b64decode(end_progress), b64decode(load_progress)
        self.temp_start, self.temp_end, self.temp_load = 'temp_start.png', 'temp_end.png', 'temp_load.gif'
        for i, j in zip([self.temp_start, self.temp_end, self.temp_load], [start, end, load]):
            file = open(i, 'wb')
            file.write(j)
            file.close()
        self.prog_start, self.prog_end = ImageTk.PhotoImage(file=self.temp_start), ImageTk.PhotoImage(file=self.temp_end)
        self.start_prog = ttk.Label(self.root, image=self.prog_start, borderwidth=0)
        self.start_prog.place(x=181, y=15)
        self.end_prog = ttk.Label(self.root, image=self.prog_end, borderwidth=0)
        self.end_prog.place(x=560, y=15)
        self.progress_bar.place(x=190, y=15)
        self.progress_lbl = ttk.Label(self.root, text=f'Generating {entry_name + ".pbt..."}', font=('montserrat', 12))
        self.progress_lbl.place(x=181, y=115)
        self.progress_uuid = ttk.Label(self.root, text=f'UUID: {uuid}', font=('montserrat', 12), foreground='#FF392B')
        self.progress_uuid.place(x=181, y=137)
        self.root.update()

    def set_wrapping_up(self, uuid, entry):
        global img
        self.some_flag = False
        self.progress_bar.place_forget(), self.progress_lbl.place_forget(), self.progress_uuid.place_forget()
        self.start_prog.place_forget(), self.end_prog.place_forget(), self.load_lbl.place_forget()
        remove(self.temp_start), remove(self.temp_end)
        self.root.update()
        self.root.geometry('210x120')
        self.central_frame.configure(width=210, height=133)
        self.central_frame.place(x=0, y=0)
        self.lbl = ttk.Label(self.central_frame, text=f'wrapping up...', font=('montserrat', 16, 'bold italic'))
        self.lbl.place(x=20, y=10)
        self.separator.place(x=10, y=47, relwidth=0.905)
        self.name_lbl = ttk.Label(self.central_frame, text=f'{entry}.pbt', font=('montserrat', 12))
        self.name_lbl.place(x=15, y=52)
        self.uuid_lbl = ttk.Label(self.central_frame, text=f'UUID: {uuid}', font=('montserrat', 12), foreground='#FF392B')
        self.uuid_lbl.place(x=15, y=75)
        self.root.update()

