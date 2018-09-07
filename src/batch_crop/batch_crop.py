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
import configparser
from datetime import datetime
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
from os.path import isfile, join
from PIL import Image, ImageTk
from sys import exit
from typing import Tuple

"""Crop files in bulk, maintaining the crop region's relative position

"""


def display_block(title: str, content: str) -> None:
    """Display a block of text in a new window

    The window is of fixed size height=30 and width=100 and has a scrollbar
    for the text.

    Args:
        title: Title of displayed window
        content: Text to display in window

    Returns:
        None

    """
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
    """Tkinter GUI app for performing batch crops of images

    Attributes:
        scale_factor (int): Factor by which original image dimensions are
            multiplied to yield the displayed image dimensions
        image_tk (ImageTk.PhotoImage): Image to display to the user for crop
            region selection
        to_crop (List[str]): The paths of all images to crop
        start_x (float): x-coordinate of one corner of the selected region
        start_y (float): y-coordinate of one corner of the selected region
        end_x (float): x-coordinate of the opposing corner of the selection
        end_y (float): y-coordinate of the opposing corner of the selection
        rect (tk.Canvas): Displayed rectangle that demarcates the selected
            region to crop
        orig_size(Tuple[float, float]): The original size of the loaded image,
            stored as ``(width, height)``
        canvas (tk.Canvas): Where the image is displayed to the user
        button_load_image (tk.Button):
        button_load_coors (tk.Button):
        button_save_coors (tk.Button):
        button_submit (tk.Button):
        button_about (tk.Button):
        button_license (tk.Button):
        button_quit (tk.Button):
        label_instructions (tk.Label):
        label_dir (tk.Label): Displays the directory of images to crop
        label_dir_label (tk.Label): Displays the label for the directory
        label_ext (tk.Label): Displays the extension of images to crop
        label_ext_label (tk.Label): Displays the label for the extension

    """

    # INSPIRATION: fhdrsdg https://stackoverflow.com/a/29797178
    def __init__(self, window: tk.Tk) -> None:
        """Setup attributes and build main user interface dialog

        Args:
            window: Root window on which to build the main UI

        """
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
        self.orig_size = None

        self.canvas = tk.Canvas(self.window, width=500, height=500)
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>", self.callback_mouse_down)
        self.canvas.bind("<B1-Motion>", self.callback_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.callback_mouse_up)

        self.button_load_image = tk.Button(self.window, text="Load Image",
                                           command=self.callback_load_image)
        self.button_load_coors = tk.Button(self.window, text="Load Coordinates",
                                           command=self.callback_load_coors)
        self.button_save_coors = tk.Button(self.window, text="Save Coordinates",
                                           command=self.callback_save_coors)
        self.button_submit = tk.Button(self.window,
                                       text="Crop All Matching Images",
                                       command=self.crop_all_files)
        self.button_about = tk.Button(self.window, text="About",
                                      command=BatchCropper.callback_about)
        self.button_license = tk.Button(self.window, text="License",
                                        command=BatchCropper.callback_license)
        self.button_quit = tk.Button(self.window, text="Quit",
                                     command=BatchCropper.callback_quit)

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
        self.button_load_coors.grid(row=4, column=0)
        self.button_save_coors.grid(row=5, column=0)
        self.button_submit.grid(row=6, column=0)
        self.button_about.grid(row=7, column=0)
        self.button_license.grid(row=8, column=0)
        self.button_quit.grid(row=9, column=0)

        self.canvas.grid(row=3, column=1, rowspan=7)

    def callback_load_image(self) -> None:
        """Load an image of the user's choice

        Meant to be triggered by tkinter when user selects a button. The user
        is allowed to choose an image, which then is displayed. All images of
        the same extension and in the same directory, including the displayed
        image, have their paths stored in :py:attr:`to_crop`. The instruction
        text is updated to tell the user to select a region.

        Returns:
            None

        """
        chosen = askopenfilename()
        dir_path = os.path.dirname(chosen)
        self.label_dir.configure(text=dir_path)
        _, extension = os.path.splitext(chosen)
        extension = extension.lower()
        self.label_ext.configure(text=extension)
        items = os.listdir(dir_path)
        files = [item for item in items if isfile(join(dir_path, item))]
        crop_names = [file for file in files
                      if file.lower().endswith(extension)]
        self.to_crop = [join(dir_path, name) for name in crop_names]

        image_raw = BatchCropper.open_image(chosen)
        self.orig_size = image_raw.size
        image_resized = self.scale_image(image_raw)

        self.image_tk = self.display_image(image_resized)
        self.label_instructions.configure(text="Select Region to Crop")

    def display_image(self, image: Image) -> ImageTk.PhotoImage:
        """Create and display an image for tkinter from a provided image

        Args:
            image: The image to process and display

        Returns:
            Image that was loaded onto the tkinter canvas

        """
        image_tk = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor="nw", image=image_tk)
        return image_tk

    def scale_image(self, image_raw: Image) -> Image:
        """Scale the provided image to fit within a 500x500 box

        The image's shape is not changed, the largest dimension is just forced
        to be 500. The factor by which the image is scaled is stored as the
        :py:attr:`scale_factor` attribute.

        Args:
            image_raw: The image to re-size

        Returns:
            The re-sized image

        """
        scale_factor = 500 / max(image_raw.size[0], image_raw.size[1])
        self.scale_factor = scale_factor
        new_width = int(image_raw.size[0] * scale_factor)
        new_height = int(image_raw.size[1] * scale_factor)
        return image_raw.resize((new_width, new_height))

    @staticmethod
    def coor_to_box(start_x: float, start_y: float, end_x: float, end_y: float)\
            -> Tuple[float, float, float, float]:
        """Convert start and end coors into left, upper, right, and lower bounds

        This is useful for converting between the Tkinter concept of start
        and end coordinates and the ``Image.crop(...)`` concept of bounds.

        Args:
            start_x: x-coordinate of one corner of the rectangle
            start_y: y-coordinate of on corner of the rectangle
            end_x: x-coordinate of the opposite corner of the rectangle
            end_y: y-coordinate of the opposite corner of the rectangle

        Returns:
            A Tuple of bounds of the form

            .. code-block:: python

               left_bound, upper_bound, right_bound, lower_bound

            that represents the region to crop. The bounds represent values on
            the same coordinate system as normal.

        """
        left = min(start_x, end_x)
        right = max(start_x, end_x)
        upper = min(start_y, end_y)
        lower = max(start_y, end_y)

        return left, upper, right, lower

    def get_coors_ratios(self) -> Tuple[float, float, float, float]:
        """Get ratios that represent the coordinates of the current region

        See :py:meth:`BatchCropper.set_coors_ratios` for an explanation of ratios.

        Returns:
            A Tuple of the ratios in the form

            .. code-block:: python

               x1, y1, x2, y2

            where ``1`` denotes ``start`` and ``2`` denotes ``end``.

        """
        x1 = self.start_x
        y1 = self.start_y
        x2 = self.end_x
        y2 = self.end_y

        x1, x2 = tuple([val / (self.orig_size[0] * self.scale_factor)
                        for val in (x1, x2)])
        y1, y2 = tuple([val / (self.orig_size[1] * self.scale_factor)
                        for val in (y1, y2)])
        return x1, y1, x2, y2

    def set_coors_ratios(self, start_x: float, start_y: float, end_x: float,
                         end_y: float) -> None:
        """Set the coordinates of the selected region from ratios

        A ``ratio`` is expressed as a fraction of the appropriate dimension.
        For example, an x-coordinate of ``30`` when the width is ``100`` is
        expressed as a ratio as ``0.3``. This allows coordinates to be
        transferred between images of varying dimensions.

        This method accepts ratios and uses them to set the selection region
        to the proper displayed coordinates as if the user had selected the
        region.

        Args:
            start_x: Ratio for the x-coordinate of one corner
            start_y: Ratio for the y-coordinate of one corner
            end_x: Ratio for the x-coordinate of the opposite corner
            end_y: Ratio for the y-coordinate of the opposite corner

        Returns:
            None

        """
        start_x, end_x = tuple([ratio * (self.orig_size[0] * self.scale_factor)
                                for ratio in (start_x, end_x)])
        start_y, end_y = tuple([ratio * (self.orig_size[1] * self.scale_factor)
                                for ratio in (start_y, end_y)])

        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y

    def callback_save_coors(self) -> None:
        """Save coordinates of the currently selected region to a file

        The user is shown a dialog to select where to save the generated INI
        file. This coordinates can be later loaded using
        :py:meth:`BatchCropper.callback_load_coors`.

        Returns:
            None

        """
        # TODO: Decompose this into UI and logic portions
        if self.to_crop is None:
            messagebox.showerror("Error", "Please load an image first.")
            return
        if self.end_x is None:
            messagebox.showerror("Error", "Please select a region first.")
            return

        start_x, start_y, end_x, end_y = self.get_coors_ratios()

        config = configparser.ConfigParser()
        config["crop-coordinates"] = {"start_x": start_x, "start_y": start_y,
                                      "end_x": end_x, "end_y": end_y}
        dir = os.path.dirname(self.to_crop[0])
        path = asksaveasfilename(title="Save Coordinates File",
                                 defaultextension=".ini",
                                 initialdir=dir)

        header = ["This file stores the coordinates of a selection made with",
                  "batch_crop.py, which is hosted at",
                  "https://github.com/U8NWXD/batch_crop",
                  "File Created: {}".format(datetime.now())]
        with open(path, "w") as configfile:
            configfile.writelines(["# " + line + "\n" for line in header])
            config.write(configfile)

    def callback_load_coors(self) -> None:
        """Load coordinates for selected region from INI file

        The user is shown a dialog to choose the file from which coordinates
        are loaded. The INI file should be created using the
        :py:meth:`BatchCropper.callback_save_coors` method. The coordinates
        specified in the file are used to create a region that is stored and
        displayed as if the user had selected it.

        Returns:
            None

        """
        # TODO: Decompose this into UI and logic portions
        if self.to_crop is None:
            messagebox.showerror("Error", "Please load an image first.")
            return

        dir = os.path.dirname(self.to_crop[0])
        path = askopenfilename(title="Select Coordinates File",
                               filetypes=[("INI", "*.ini")],
                               initialdir=dir)

        config = configparser.ConfigParser()
        config.read(path)
        try:
            coor_conf = config["crop-coordinates"]
        except KeyError:
            messagebox.showerror("Error", "'{}' could not be parsed".
                                 format(path))
            return
        # Remember these are fractions of the total image dimensions
        start_x = float(coor_conf.getfloat("start_x", fallback=-1))
        start_y = float(coor_conf.getfloat("start_y", fallback=-1))
        end_x = float(coor_conf.getfloat("end_x", fallback=-1))
        end_y = float(coor_conf.getfloat("end_y", fallback=-1))

        if start_x == -1 or start_y == -1 or end_x == -1 or end_y == -1:
            messagebox.showerror("Error", "'{}' could not be parsed.".
                                 format(path))

        self.set_coors_ratios(start_x, start_y, end_x, end_y)

        self.make_or_reuse_rect(self.start_x, self.start_y)
        self.resize_rect(self.start_x, self.start_y, self.end_x, self.end_y)

    def callback_mouse_down(self, event) -> None:
        """Start drawing out a rectangle

        The rectangle is started using :py:meth:`BatchCropper.make_or_reuse_rect`.

        This callback is meant to be bound using
        Tkinter to the mouse move event. Tkinter will then pass the
        needed ``event`` parameter as it calls this method whenever the mouse
        moves.

        Args:
            event: The event from Tkinter that has attributes ``.x`` and ``.y``
                that hold the coordinates of the cursor when mouse released

        Returns:
            None

        """
        self.start_x = event.x
        self.start_y = event.y
        self.end_x = None
        self.end_y = None
        self.make_or_reuse_rect(self.start_x, self.start_y)

    def make_or_reuse_rect(self, x: float, y: float) -> None:
        """Create a new rectangle or reset one if it already exists

        The created or reset rectangle will have identical start and end
        coordinates.

        Args:
            x: x-coordinate for both start and end corners of rectangle
            y: y-coordinate for both start and end corners of rectangle

        Returns:
            None

        """
        if self.rect is None:
            self.rect = self.canvas.create_rectangle(x, y, x, y, outline="red")
        else:
            self.resize_rect(x, y, x, y)

    def callback_mouse_move(self, event) -> None:
        """Expand the displayed selected region to follow the cursor

        This allows the user to drag out the rectangle. The rectangle is only
        changed if the mouse button is down (checked by member variables
        :py:attr:`end_x` and :py:attr:`end_y` being ``None`` if button down).

        This callback is meant to be bound using
        Tkinter to the mouse move event. Tkinter will then pass the
        needed ``event`` parameter as it calls this method whenever the mouse
        moves.

        Args:
            event: The event from Tkinter that has attributes ``.x`` and ``.y``
                that hold the coordinates of the cursor when mouse released

        Returns:
            None

        """
        cur_x = event.x
        cur_y = event.y

        if self.end_x is None and self.end_y is None:
            self.resize_rect(self.start_x, self.start_y, cur_x, cur_y)

    @staticmethod
    def callback_quit() -> None:
        """Exit with code ``0``

        Returns:
            None

        """
        exit(0)

    @staticmethod
    def callback_about() -> None:
        """Display the project's about text as stored in :file:about.txt

        See :py:meth:`display_block` for the details of how the text is displayed.

        Returns:
            None

        """
        with open("about.txt", "r") as f:
            about_text = f.read()
        display_block("About", about_text)

    @staticmethod
    def callback_license() -> None:
        """Display the project's license as stored in :file:LICENSE.txt

        See :py:meth:`display_block` for the details of how the text is displayed.

        Returns:
            None

        """
        with open("LICENSE.txt", "r") as f:
            license_text = f.read()
        display_block("License", license_text)

    def resize_rect(self, x1: float, y1: float, x2: float, y2: float) -> None:
        """Change coordinates of region selection rectangle

        The region selection rectangle is the red rectangle that represents the
        region to be cropped

        Args:
            x1: x-coordinate of first corner
            y1: y-coordinate of first corner
            x2: x-coordinate of opposite corner
            y2: y-coordinate of opposite corner

        Returns:
            None
        """
        self.canvas.coords(self.rect, x1, y1, x2, y2)

    def callback_mouse_up(self, event) -> None:
        """Save event coordinates as end coordinates and update instructions

        Store the x and y coordinates of ``event`` to the ``end_x`` and
        ``end_y`` instance variables. This callback is meant to be bound using
        Tkinter to the mouse button up event. Tkinter will then pass the
        needed ``event`` parameter as it calls this method whenever the mouse
        button is released.

        Args:
            event: The event from Tkinter that has attributes ``.x`` and ``.y``
                that hold the coordinates of the cursor when mouse released

        Returns:
            None

        """
        self.end_x = event.x
        self.end_y = event.y
        self.label_instructions.configure(text="Re-select Region or Crop All")

    @staticmethod
    def open_image(path: str) -> Image:
        """Attempt to open an image, using a method appropriate for the format

        Supported image types: RAW / ARW and those supported by Pillow.
        Errors are not handled. Format is determined by file extension.

        Args:
            path: Path to the image. Must correctly point to a supported image
                type.

        Returns:
            A Pillow Image object loaded from ``path``

        """
        base, ext = os.path.splitext(path)
        ext = ext.lower()
        if ext == ".arw" or ext == ".raw":
            image = BatchCropper.open_raw_image(path)
        else:
            image = Image.open(path)

        return image

    @staticmethod
    def open_raw_image(path: str) -> Image:
        """Open RAW-formatted image using ``rawpy``

        No format checking or error handling is performed.

        Args:
            path: Path to the image. Must be correct.

        Returns:
            A Pillow Image object representing the image at ``path``

        """
        with rawpy.imread(path) as raw:
            mat = raw.postprocess()
        return Image.fromarray(mat)

    def crop_all_files(self) -> None:
        """Crop all files at the paths in the ``to_crop`` instance variable

        Validates that the user has selected a region. Cropping is aborted
        if :py:meth:`BatchCropper.crop_file` returns ``False``. See
        :py:meth:`BatchCropper.crop_file` for details on the cropping itself.

        Returns:
            None

        """
        if self.end_x is None or self.end_y is None:
            messagebox.showerror("Error", "Please select a region to crop.")
        else:
            for path in self.to_crop:
                continue_cropping = self.crop_file(path)
                if not continue_cropping:
                    return

    def crop_file(self, path: str) -> bool:
        """Save a copy of an image cropped to the region the user chose

        Crops the image at ``path`` to the same relative region as the user
        selected on the template image. For example, if the selected region
        takes up the middle ninth (in a 3x3 grid of equivalent rectangles) of
        the image, the crop will be the middle ninth of the image at ``path``,
        even if the two images have different dimensions.

        No validation is performed on ``path``. The user is asked to confirm,
        skip, or abort before any file is over-written. The return value is used
        to distinguish between aborting and skipping.

        The cropped image is formatted as a JPEG.

        Args:
            path: The filepath of the image to crop

        Returns:
            ``True`` if cropping should continue, ``False`` otherwise.

        """
        to_crop = BatchCropper.open_image(path)

        left, upper, \
        right, lower = BatchCropper.coor_to_box(self.start_x, self.start_y,
                                                self.end_x, self.end_y)

        left, upper, right, lower = tuple([val / self.scale_factor for val in
                                           (left, upper, right, lower)])
        left, right = tuple([val * to_crop.size[0] / self.orig_size[0]
                             for val in (left, right)])
        upper, lower = tuple([val * to_crop.size[1] / self.orig_size[1]
                              for val in (upper, lower)])

        cropped = to_crop.crop((left, upper, right, lower))
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
