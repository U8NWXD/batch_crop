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
from os.path import isfile, join
from PIL import Image, ImageTk
from sys import argv, exit
from typing import List


class BatchCropper(tk.Frame):
    # INSPIRATION: fhdrsdg https://stackoverflow.com/a/29797178
    def __init__(self, window, image, to_crop: List[str]):
        tk.Frame.__init__(self, window)
        self.to_crop = to_crop
        self.scale_factor = 1
        image = self.scale_image(image)
        self.canvas = tk.Canvas(window, width=image.size[0],
                                height=image.size[1])
        self.canvas.pack()
        self.image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="ne", image=self.image)

        self.canvas.bind("<ButtonPress-1>", self.callback_mouse_down)
        self.canvas.bind("<B1-Motion>", self.callback_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.callback_mouse_up)

        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect = None

        self.button_submit = tk.Button(window, text="Crop All",
                                       command=self.crop_all_files)

        self.canvas.grid(row=0, column=0)
        self.button_submit.grid(row=1, column=0)

    @classmethod
    def from_file(cls, window, path, to_crop: List[str]):
        image = BatchCropper.open_image(path)
        return cls(window, image, to_crop)

    def scale_image(self, image):
        scale_factor = 500 / max(image.size[0], image.size[1])
        self.scale_factor = scale_factor
        new_width = int(image.size[0] * scale_factor)
        new_height = int(image.size[1] * scale_factor)
        return image.resize((new_width, new_height))

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

    def resize_rect(self, x1, y1, x2, y2):
        self.canvas.coords(self.rect, x1, y1, x2, y2)

    def callback_mouse_up(self, event):
        self.end_x = event.x
        self.end_y = event.y

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

    def crop_all_files(self):
        for path in self.to_crop:
            self.crop_file(path)

    def crop_file(self, path):
        to_crop = BatchCropper.open_image(path)

        left = min(self.start_x, self.end_x)
        right = max(self.start_x, self.end_x)
        upper = min(self.start_y, self.end_y)
        lower = max(self.start_y, self.end_y)
        box = left, upper, right, lower

        cropped = to_crop.crop(tuple([val / self.scale_factor for val in box]))
        cropped.save(path + "_cropped.jpg", "jpeg")


if __name__ == "__main__":
    if len(argv) != 3:
        print("Invalid parameters. Usage: batch_crop.py dir_path extension")
        exit(1)

    dir_path = os.path.abspath(argv[1])
    extension = argv[2]
    items = os.listdir(dir_path)
    files = [item for item in items if isfile(join(dir_path, item))]
    crop_names = [file for file in files if file.endswith("." + extension)]
    crop_paths = [join(dir_path, name) for name in crop_names]

    master = tk.Tk()
    app = BatchCropper.from_file(master, crop_paths[0], crop_paths)
    app.master.title("batch_crop")
    master.mainloop()
