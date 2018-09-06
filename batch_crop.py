# This file is part of batch_crop: A Python utility for batch cropping images
# Copyright (C) 2018  U8N WXD <cs.temporary@icloud.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import tkinter as tk
import rawpy
import os
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from os.path import isfile, join
from PIL import Image, ImageTk
from sys import argv, exit
from typing import List


def display_block(title, content):
    def close():
        second.destroy()

    second = tk.Tk()
    second.wm_title(title)

    S = tk.Scrollbar(second)
    T = tk.Text(second, height=30, width=100, wrap='word')
    B = tk.Button(second, text='Close', command=close)

    S.pack(side=tk.RIGHT, fill=tk.Y)
    T.pack(side=tk.LEFT, fill=tk.Y)
    B.pack(side=tk.BOTTOM)

    S.config(command=T.yview)
    T.config(yscrollcommand=S.set)

    T.insert(tk.END, content)

    second.mainloop()


class BatchCropper(tk.Frame):
    # INSPIRATION: fhdrsdg https://stackoverflow.com/a/29797178
    def __init__(self, window):
        tk.Frame.__init__(self, window)
        self.window = window

        # Initialize instance fields for later
        self.scale_factor = 1
        self.image_tk = None
        self.to_crop = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None

        self.canvas = tk.Canvas(self.window, width=500, height=500)
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>", self.callback_mouse_down)
        self.canvas.bind("<B1-Motion>", self.callback_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.callback_mouse_up)

        self.button_submit = tk.Button(self.window,
                                       text="Crop All Matching Images",
                                       command=self.crop_all_files)
        self.button_quit = tk.Button(self.window, text="Quit",
                                     command=BatchCropper.callback_quit)
        self.button_about = tk.Button(self.window, text="About",
                                      command=BatchCropper.callback_about)
        self.button_load_image = tk.Button(self.window, text="Load Image",
                                           command=self.callback_load_image)
        self.button_license = tk.Button(self.window, text="License",
                                        command=BatchCropper.callback_license)

        self.label_instructions = tk.Label(self.window, text="Select an Image")
        self.label_dir = tk.Label(self.window, text="")
        self.label_dir_label = tk.Label(self.window,
                                        text="Directory of Images to Crop: ")
        self.label_ext = tk.Label(self.window, text="")
        self.label_ext_label = tk.Label(self.window,
                                        text="Extension of Images to Crop: ")

        # Arrange UI elements
        self.label_instructions.grid(row=0, column=0, columnspan=2)

        self.label_dir_label.grid(row=1, column=0)
        self.label_dir.grid(row=1, column=1)

        self.label_ext_label.grid(row=2, column=0)
        self.label_ext.grid(row=2, column=1)

        self.button_load_image.grid(row=3, column=0)
        self.button_submit.grid(row=4, column=0)
        self.button_about.grid(row=5, column=0)
        self.button_license.grid(row=6, column=0)
        self.button_quit.grid(row=7, column=0)

        self.canvas.grid(row=3, column=1, rowspan=5)

    def callback_load_image(self):
        chosen = askopenfilename()
        dir_path = os.path.dirname(chosen)
        self.label_dir.configure(text=dir_path)
        _, extension = os.path.splitext(chosen)
        extension = extension.lower()
        self.label_ext.configure(text=extension)
        items = os.listdir(dir_path)
        files = [item for item in items if isfile(join(dir_path, item))]
        crop_names = [file for file in files if file.lower().endswith(extension)]
        self.to_crop = [join(dir_path, name) for name in crop_names]

        image_raw = BatchCropper.open_image(chosen)
        image_resized = self.scale_image(image_raw)

        self.image_tk = self.display_image(image_resized)
        self.label_instructions.configure(text="Select Region to Crop")

    def display_image(self, image):
        image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=image_tk)
        return image_tk

    def scale_image(self, image_raw):
        scale_factor = 500 / max(image_raw.size[0], image_raw.size[1])
        self.scale_factor = scale_factor
        new_width = int(image_raw.size[0] * scale_factor)
        new_height = int(image_raw.size[1] * scale_factor)
        return image_raw.resize((new_width, new_height))

    def callback_mouse_down(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.end_x = None
        self.end_y = None
        if self.rect is None:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y,
                                                     self.start_x, self.start_y,
                                                     outline="red")
        else:
            self.resize_rect(self.start_x, self.start_y,
                             self.start_x, self.start_y)

    def callback_mouse_move(self, event):
        cur_x = event.x
        cur_y = event.y

        if self.end_x is None and self.end_y is None:
            self.resize_rect(self.start_x, self.start_y, cur_x, cur_y)

    @staticmethod
    def callback_quit():
        exit(0)

    @staticmethod
    def callback_about():
        with open("about.txt", "r") as f:
            about_text = f.read()
        display_block("About", about_text)

    @staticmethod
    def callback_license():
        with open("LICENSE.txt", "r") as f:
            license_text = f.read()
        display_block("License", license_text)

    def resize_rect(self, x1, y1, x2, y2):
        self.canvas.coords(self.rect, x1, y1, x2, y2)

    def callback_mouse_up(self, event):
        self.end_x = event.x
        self.end_y = event.y
        self.label_instructions.configure(text="Re-select Region or Crop All")

    @staticmethod
    def open_image(path):
        base, ext = os.path.splitext(path)
        ext = ext.lower()
        if ext == ".arw" or ext == ".raw":
            image = BatchCropper.open_raw_image(path)
        else:
            image = Image.open(path)

        return image

    @staticmethod
    def open_raw_image(path):
        with rawpy.imread(path) as raw:
            mat = raw.postprocess()
        return Image.fromarray(mat)

    def crop_all_files(self) -> None:
        if self.end_x is None or self.end_y is None:
            messagebox.showerror("Error", "Please select a region to crop.")
        else:
            for path in self.to_crop:
                continue_cropping = self.crop_file(path)
                if not continue_cropping:
                    return

    def crop_file(self, path) -> bool:
        to_crop = BatchCropper.open_image(path)

        left = min(self.start_x, self.end_x)
        right = max(self.start_x, self.end_x)
        upper = min(self.start_y, self.end_y)
        lower = max(self.start_y, self.end_y)
        box = left, upper, right, lower

        cropped = to_crop.crop(tuple([val / self.scale_factor for val in box]))
        new_path = path + "_cropped.jpg"
        if os.path.exists(new_path):
            message = "The file '{}' already exists. Overwrite with new " \
                      "crop? Select 'Cancel' to abort, 'No' to skip, or " \
                      "'Yes' to overwrite."
            message = message.format(new_path)
            choice = messagebox.askyesnocancel("Overwrite Warning", message)
            if choice is None:
                return False
            elif choice:
                cropped.save(new_path, "jpeg")
                return True
            else:
                return True
        else:
            cropped.save(new_path, "jpeg")
            return True


if __name__ == "__main__":
    master = tk.Tk()
    app = BatchCropper(master)
    app.master.title("batch_crop")
    master.mainloop()
