from tkinter import *
from tkinter import ttk, colorchooser, messagebox
import time
import threading
from colorhash import ColorHash
from os import path
import json


class PaintMain:
    def __init__(self, master):
        self.individual_list = []
        self.vectX = []
        self.vectY = []
        self.vectT = []
        self.master = master
        self.color_fg = self.get_color(0)
        self.color_bg = 'white'
        self.old_x = None
        self.old_y = None
        self.penwidth = 5
        self.drawWidgets()
        self.c.bind('<B1-Motion>', self.paint)  # drwaing the line
        self.c.bind('<Button-1>', self.time_progression)
        self.c.bind('<ButtonRelease-1>', self.reset)
        self.c.bind('<Button-3>', self.clear_individual)
        self.master.bind('<Delete>', self.remove_individual)
        self.master.bind('n', self.add_individual)
        self.time_thread = None
        self.time_pressed = None
        self.txtPath = r'Simulated Data.txt'
        self.jsonPath = r'simulated_tracks.json'
        self.framerate = 30

        self.save_dict = {}

        if not path.exists(self.txtPath):
            with open(self.txtPath, 'w+') as f:
                pass

    def time_progression(self, e):
        self.clear_individual(self.var.get())
        self.delete_individuals_data(self.var.get())
        self.time_pressed = time.time()
        self.time_thread = threading.Thread(target=self.time_thread_func, daemon=True)
        self.time_thread.start()

    def time_thread_func(self):
        tmax = float(self.time_txt.get()) * 0.91
        t_step = tmax / 100
        for i in range(100):
            if i < self.progressbar["value"]:
                self.progressbar.step(99 - i)
                break
            time.sleep(t_step)
            self.progressbar.step()

    def paint(self, e):
        if time.time() - self.time_pressed < float(self.time_txt.get()):
            if self.old_x and self.old_y:
                e.widget.create_line(self.old_x, self.old_y, e.x, e.y, width=self.penwidth, fill=self.color_fg,
                                     capstyle=ROUND, smooth=True, tag=("Individual" + str(self.var.get())))
            self.old_x = e.x
            self.old_y = e.y
            self.vectX.append(e.x)
            self.vectY.append(e.y)
            self.vectT.append(time.time() - self.time_pressed)

    def reset(self, e):  # resetting or cleaning the canvas
        if self.time_thread.is_alive():
            self.progressbar.step(1)
        self.old_x = None
        self.old_y = None
        '''if min(self.vectX) < 0 or min(self.vectY) < 0 or max(self.vectX) > self.c.winfo_width() - 1 or \
                max(self.vectY) > self.c.winfo_height() - 1:
            self.vectX = []
            self.vectY = []
            raise Exception("Drawing outside of canvas borders!")'''
        self.save_data(self.vectX, self.vectY, self.vectT, self.var.get())
        self.vectX = []
        self.vectY = []
        self.vectT = []

    @staticmethod
    def get_color(seed):
        return ColorHash(str(seed) + 'noise...!!').hex

    def sel(self):
        print("Selected value: " + str(self.var.get()))
        self.color_fg = self.get_color(self.var.get())

    def save_data(self, x, y, t, n):
        self.save_dict[str(n)] = {}
        paint_vect = list(zip(self.vectX, self.vectY, self.vectT))
        n_frames = int(paint_vect[-1][2] * self.framerate + 1)
        data_vect = []
        current_time = 0
        for frame_no in range(n_frames):
            while frame_no/self.framerate > paint_vect[current_time][2] and frame_no < n_frames - 1:
                current_time += 1

            data_vect.append((paint_vect[current_time][0], paint_vect[current_time][1], frame_no))

            self.save_dict[str(n)][str(frame_no)] = [paint_vect[current_time][0], paint_vect[current_time][1]]

        with open(self.jsonPath, 'w+') as fp:
            json.dump(self.save_dict, fp, indent=2)

        with open(self.txtPath, 'a') as f:
            f.write('Individual No. ' + str(n) + '\n')
            f.write(str(data_vect) + '\n')

        print(len(data_vect))

    def delete_individuals_data(self, n):
        skp = False
        with open(self.txtPath, "r") as f:
            lines = f.readlines()
        with open(self.txtPath, "w") as f:
            for line in lines:
                if line.strip("\n") != ("Individual No. " + str(n)) and not skp:
                    f.write(line)
                    skp = False
                elif line.strip("\n") == ("Individual No. " + str(n)):
                    skp = True
                else:
                    skp = False

    def add_individual(self, e=None):
        if len(self.individual_list) == 0:
            val = 0
        else:
            val = self.individual_list[-1]['value'] + 1
        self.individual_list.append(
            Radiobutton(self.controls, text=("Individual No. " + str(val)),
                        indicatoron=0, width=15, variable=self.var, value=val, command=self.sel))
        self.individual_list[-1].pack(anchor=W)
        self.individual_list[-1].invoke()

    def remove_individual(self, e=None):
        temp = None
        for i in self.individual_list:
            if i['value'] == self.var.get():
                temp = i
                break

        if temp == self.individual_list[0]:
            print("Can't destroy Individual No. 0!")
        else:
            print('Destroying Individual No. ' + str(self.var.get()))
            self.clear_individual()
            self.individual_list.remove(temp)
            temp.destroy()

            self.individual_list[-1].invoke()

    def clear_individual(self, e=None):
        self.c.delete("Individual" + str(self.var.get()))
        self.delete_individuals_data(self.var.get())

    def clear(self, e=None):
        if messagebox.askquestion('Clear All', 'Are you sure you want clear the canvas', icon='warning') == 'yes':
            self.c.delete(ALL)
        with open(self.txtPath, 'w+') as f:
            f.write('')

    def change_fg(self):  # changing the pen color
        self.color_fg = colorchooser.askcolor(color=self.color_fg)[1]

    def change_bg(self):  # changing the background color canvas
        self.color_bg = colorchooser.askcolor(color=self.color_bg)[1]
        self.c['bg'] = self.color_bg

    def drawWidgets(self):
        self.controls = Frame(self.master, padx=5, pady=5)
        self.controls.pack(side=LEFT)

        self.timebar = Frame(self.master, padx=5, pady=5)
        self.timebar.pack(side=BOTTOM)
        self.secbar = Frame(self.timebar, padx=5, pady=5)
        self.secbar.pack(side=RIGHT)

        self.progressbar = ttk.Progressbar(self.timebar, orient=HORIZONTAL, length=450, mode='determinate')
        self.progressbar.pack(side=LEFT)
        self.time_txt = Entry(self.secbar, width=10)
        self.time_txt.insert(END, '3')
        self.time_txt.pack(side=LEFT)
        self.l1 = Label(self.secbar, text='sec')
        self.l1.pack(side=RIGHT)

        self.var = IntVar()

        self.add_individual()

        self.c = Canvas(self.master, width=500, height=400, bg=self.color_bg, )
        self.c.pack(fill=BOTH, expand=True)

        menu = Menu(self.master)
        self.master.config(menu=menu)
        menu.add_command(label='Background Color', command=self.change_bg)
        menu.add_command(label='Clear Canvas', command=self.clear)
        menu.add_command(label='Add Individual', command=self.add_individual)
        menu.add_command(label='Remove Selected Individual', command=self.remove_individual)


if __name__ == '__main__':
    root = Tk()
    PaintMain(root)
    root.title('Trajectory Simulator')
    root.mainloop()
