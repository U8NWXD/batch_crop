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


"""Crop files in bulk, maintaining the crop region's relative position

"""

import os
from os.path import isfile, join
import configparser
from datetime import datetime
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
from typing import Tuple, List

import rawpy
from PIL import Image, ImageTk


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

    scroll_bar = tk.Scrollbar(second)
    text = tk.Text(second, height=30, width=100, wrap='word')
    close_button = tk.Button(second, text='Close', command=close)

    scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
    text.pack(side=tk.LEFT, fill=tk.Y)
    close_button.pack(side=tk.BOTTOM)

    scroll_bar.config(command=text.yview)
    text.config(yscrollcommand=scroll_bar.set)

    text.insert(tk.END, content)

    second.mainloop()


# pylint: disable=too-many-instance-attributes, too-many-ancestors


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
        self.scale_factor = 1  # type: float
        self.image_tk = None  # type: ImageTk.PhotoImage
        self.to_crop = []  # type: List[str]
        self.start_x = -1  # type: float
        self.start_y = -1  # type: float
        self.end_x = -1  # type: float
        self.end_y = -1  # type: float
        self.rect = None  # type: ignore
        self.orig_size = -1, -1  # type: Tuple[float, float]

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
                                       command=self.callback_crop)
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

        image_raw = open_image(chosen)
        self.orig_size = image_raw.size
        self.scale_factor = get_scale_factor(500, image_raw)
        image_resized = scale_image(self.scale_factor, image_raw)

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

    def get_coors_ratios(self) -> Tuple[float, float, float, float]:
        """Get ratios that represent the coordinates of the current region

        For definitions of coordinates and ratios, see :doc:`units`

        Returns:
            A box_ratio that represents the current region

        """
        coors = self.start_x, self.start_y, self.end_x, self.end_y

        width, height = self.orig_size
        disp_size = (width * self.scale_factor, height * self.scale_factor)

        return coors_to_ratios(disp_size, coors)

    def set_coors_ratios(self, box_ratio: Tuple[float, float, float, float]) \
            -> None:
        """Set the coordinates of the selected region from ratios

        For definitions of coordinates and ratios, see :doc:`units`

        This method accepts ratios and uses them to set the selection region
        to the proper displayed coordinates as if the user had selected the
        region.

        Args:
            box_ratio: The ``box_ratio`` to use

        Returns:
            None

        """
        width = self.orig_size[0] * self.scale_factor
        height = self.orig_size[1] * self.scale_factor
        size = (width, height)

        coors = ratios_to_coors(size, box_ratio)
        self.start_x, self.start_y, self.end_x, self.end_y = coors

    def callback_save_coors(self) -> None:
        """Save coordinates of the currently selected region to a file

        The user is shown a dialog to select where to save the generated INI
        file. This coordinates can be later loaded using
        :py:meth:`BatchCropper.callback_load_coors`.

        The coordinates are actually saved as a ``box_ratio``, which is
        generated by :py:meth:`BatchCropper.get_coors_ratios`. The file is
        created and saved by :py:meth:`save_ratios_to_file`.

        Error dialogs are displayed if no image is loaded or if no region
        is selected.

        Returns:
            None

        """
        if len(self.to_crop) == 0:  # pylint: disable=len-as-condition
            messagebox.showerror("Error", "Please load an image first.")
            return
        if self.end_x < 0 or self.end_y < 0:
            messagebox.showerror("Error", "Please select a region first.")
            return

        box_ratio = self.get_coors_ratios()
        path = asksaveasfilename(title="Save Coordinates File",
                                 defaultextension=".ini",
                                 initialdir=os.path.dirname(self.to_crop[0]))
        save_ratios_to_file(box_ratio, path)

    def callback_load_coors(self) -> None:
        """Load coordinates for selected region from INI file

        The user is shown a dialog to choose the file from which coordinates
        are loaded. The INI file should be created using the
        :py:meth:`BatchCropper.callback_save_coors` method. The coordinates
        specified in the file are used to create a region that is stored and
        displayed as if the user had selected it.

        Error dialogs are displayed if no image is loaded or if the
        configuration file cannot be parsed.

        The configuration file is read with :py:meth:`get_ratios_from_file`,
        which yields a ``box_ratio`` (see :doc:`units`) that is then loaded
        using :py:meth:`BatchCropper.set_coors_ratios`.

        Returns:
            None

        """
        if len(self.to_crop) == 0:  # pylint: disable=len-as-condition
            messagebox.showerror("Error", "Please load an image first.")
            return

        path = askopenfilename(title="Select Coordinates File",
                               filetypes=[("INI", "*.ini")],
                               initialdir=os.path.dirname(self.to_crop[0]))

        try:
            ratios = get_ratios_from_file(path)
        except KeyError:
            messagebox.showerror("Error", "'{}' could not be parsed".
                                 format(path))
            return

        self.set_coors_ratios(ratios)
        self.make_or_reuse_rect(self.start_x, self.start_y)
        self.resize_rect(self.start_x, self.start_y, self.end_x, self.end_y)

    def callback_mouse_down(self, event) -> None:
        """Start drawing out a rectangle

        The rectangle is started using
        :py:meth:`BatchCropper.make_or_reuse_rect`.

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
        self.end_x = -1
        self.end_y = -1
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

        See :py:meth:`display_block` for the details of how the text is
        displayed.

        Returns:
            None

        """
        with open("about.txt", "r") as f:
            about_text = f.read()
        display_block("About", about_text)

    @staticmethod
    def callback_license() -> None:
        """Display the project's license as stored in :file:LICENSE.txt

        See :py:meth:`display_block` for the details of how the text is
        displayed.

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

    def callback_crop(self) -> None:
        """Trigger the cropping of all images

        Checks if a region is selected, then triggers
        :py:meth:`BatchCropper.crop_all_files`.

        Returns:
            None

        """
        if self.end_x is None or self.end_y is None:
            messagebox.showerror("Error", "Please select a region to crop.")
        else:
            self.crop_all_files()

    def crop_all_files(self) -> None:
        """Crop all files at the paths in :py:attr:`to_crop`

        Validates that the user has selected a region.

        No validation is performed on :py:attr:`to_crop`. The user is asked to
        confirm, skip, or abort before any file is over-written.

        Each file is cropped using :py:meth:`crop_file`

        Returns:
            None

        """
        for path in self.to_crop:
            new_path = path + "_cropped.jpg"
            if os.path.exists(new_path):
                message = "The file '{}' already exists. Overwrite with new " \
                          "crop? Select 'Cancel' to abort, 'No' to skip, or " \
                          "'Yes' to overwrite."
                message = message.format(new_path)
                choice = messagebox.askyesnocancel("Overwrite Warning", message)
                if choice is None:
                    return
                if choice:
                    crop_file(self.get_coors_ratios(), path, new_path)
            else:
                crop_file(self.get_coors_ratios(), path, new_path)


def crop_file(box_ratio: Tuple[float, float, float, float],
              in_path: str, out_path: str) -> None:
    """Save a copy of an image cropped to a specified region

    Crops the image at ``in_path`` to the same relative region as the user
    selected on the template image. For example, if the selected region
    takes up the middle ninth (in a 3x3 grid of equivalent rectangles) of
    the image, the crop will be the middle ninth of the image at ``path``,
    even if the two images have different dimensions.

    No validation is performed on ``in_path``.

    The cropped image is formatted as a JPEG and saved to ``out_path``. Any
    existing file at ``out_path`` may be overwritten.

    The cropped image is created using :py:meth:`crop_image`.

    Args:
        box_ratio: A ``box_ratio`` (See :doc:`units`) that describes the region
            to crop
        in_path: The path of the image to crop
        out_path: The path of the file to save the cropped image to

    Returns:
        ``True`` if cropping should continue, ``False`` otherwise.

    """
    to_crop = open_image(in_path)
    cropped = crop_image(box_ratio, to_crop)
    cropped.save(out_path, "jpeg")


def crop_image(box_ratio: Tuple[float, float, float, float], image: Image):
    """Generate a copy of an image cropped to a specified region

    Args:
        box_ratio: A ``box_ratio`` (See :doc:`units`) that defines the region to
            crop
        image: The image to crop

    Returns:
        The cropped image

    """
    box_coor = ratios_to_coors(image.size, box_ratio)
    box = coor_to_box(box_coor)
    cropped = image.crop(box)
    return cropped


def scale_image(scale_factor: float, image_raw: Image) -> Image:
    """Scale the provided image to fit within a 500x500 box

    The image's shape is not changed, the largest dimension is just forced
    to be 500. The factor by which the image is scaled is stored as the
    :py:attr:`scale_factor` attribute.

    Args:
        scale_factor: The factor by which the image's width and height are
            re-sized
        image_raw: The image to re-size

    Returns:
        The re-sized image

    """
    width, height = image_raw.size
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    return image_raw.resize((new_width, new_height))


def get_scale_factor(max_dimen: float, image_raw: Image) -> float:
    """Get the factor by which to scale ``image_raw`` based on ``max_dimen``

    Args:
        max_dimen: What to scale the largest dimension of the image to
        image_raw: The image to scale

    Returns:
        The scaled image

    """
    width, height = image_raw.size
    return max_dimen / max(width, height)


def coor_to_box(coors: Tuple[float, float, float, float])\
        -> Tuple[float, float, float, float]:
    """Convert start and end coors into left, upper, right, and lower bounds

    This is useful for converting between the Tkinter concept of start
    and end coordinates and the ``Image.crop(...)`` concept of bounds.

    >>> coors = (5, 3, 1, 2)
    >>> coor_to_box(coors)
    (1, 2, 5, 3)


    Args:
        coors: The ``box_coor`` to convert to a ``box``

    Returns:
        A Tuple of bounds of the form

        .. code-block:: python

           left_bound, upper_bound, right_bound, lower_bound

        that represents the region to crop. The bounds represent values on
        the same coordinate system as normal.

    """
    start_x, start_y, end_x, end_y = coors
    left = min(start_x, end_x)
    right = max(start_x, end_x)
    upper = min(start_y, end_y)
    lower = max(start_y, end_y)

    return left, upper, right, lower


def coors_to_ratios(image_size: Tuple[float, float],
                    coors: Tuple[float, float, float, float])\
        -> Tuple[float, float, float, float]:
    """Convert a ``box_coor`` to a ``box_ratio``

    >>> image_size = 10, 100
    >>> coors = 1, 2, 5, 4
    >>> coors_to_ratios(image_size, coors)
    (0.1, 0.02, 0.5, 0.04)

    Args:
        image_size: The size of the image that is the context for ``coors``
        coors: ``box_coor`` to convert

    Returns:
        The ``box_ratio``

    """
    x1, y1, x2, y2 = coors
    width, height = image_size
    x1, x2 = tuple([val / width for val in (x1, x2)])
    y1, y2 = tuple([val / height for val in (y1, y2)])
    return x1, y1, x2, y2


def ratios_to_coors(image_size: Tuple[float, float],
                    ratios: Tuple[float, float, float, float]) -> \
        Tuple[float, float, float, float]:
    """Convert a ``box_ratio`` to a ``box_coor``

    Args:
        image_size: Size of image that is the context for ``box_coor``
        ratios: The ``box_ratio`` to convert

    Returns:
        The ``box_coor``

    """
    x1, y1, x2, y2 = ratios
    width, height = image_size
    x1, x2 = tuple([ratio * width for ratio in (x1, x2)])
    y1, y2 = tuple([ratio * height for ratio in (y1, y2)])

    return x1, y1, x2, y2


def gen_ratios_config(box_ratio: Tuple[float, float, float, float]) \
        -> configparser.ConfigParser:
    """Create the configuration that stores the provided box

    The configuration is stored under the section ``crop-coordinates`` in the
    following format INI, given ``box_ratio = (x1, y1, x2, y2)``:

    .. code-block:: ini

       [crop-coordinates]
       start_x = {x1}
       start_y = {y2}
       end_x = {x2}
       end_y = {y2}

    substituting ``{...}`` for the value of the variable in braces.

    Args:
        box_ratio: The box_ratio to generate a configuration for

    Returns:
        The configuration

    """
    start_x, start_y, end_x, end_y = box_ratio
    config = configparser.ConfigParser()
    config["crop-coordinates"] = {"start_x": str(start_x),
                                  "start_y": str(start_y),
                                  "end_x": str(end_x),
                                  "end_y": str(end_y)}
    return config


def save_ratios_to_file(box_ratio: Tuple[float, float, float, float],
                        path: str) -> None:
    """Save the configuration for the ``box_ratio`` to the specified INI file

    The configuration is generated by :py:meth:`gen_coors_config`.

    Args:
        box_ratio: The ``box_ratio`` to store in the file
        path: The path to the INI file to store the configuration in. The file
            should be empty.

    Returns:
        None

    """
    config = gen_ratios_config(box_ratio)
    header = ["This file stores the coordinates of a selection made with",
              "batch_crop.py, which is hosted at",
              "https://github.com/U8NWXD/batch_crop",
              "File Created: {}".format(datetime.now())]
    with open(path, "w") as configfile:
        configfile.writelines(["# " + line + "\n" for line in header])
        config.write(configfile)


def get_ratios_from_file(path: str) -> Tuple[float, float, float, float]:
    """Get a ``box_ratio`` from a configuration file

    The configuration file should have been generated by
    :py:meth:`save_ratios_to_file`. The configuration in the file is converted
    to a ``box_ratio`` by :py:meth:`get_ratios_from_config`.

    Args:
        path: Path to configuration INI file

    Returns:
        ``box_ratio`` that was described by the file

    """
    config = configparser.ConfigParser()
    config.read(path)
    return get_ratios_from_config(config)


def get_ratios_from_config(config: configparser.ConfigParser) \
        -> Tuple[float, float, float, float]:
    """Get a ``box_ratio`` from a configuration

    Args:
        config: INI configuration describing the ``box_ratio`` to read

    Returns:
        ``box_ratio`` described by the configuration

    """
    coor_conf = config["crop-coordinates"]
    # Remember these are ratios
    start_x = coor_conf.getfloat("start_x")
    start_y = coor_conf.getfloat("start_y")
    end_x = coor_conf.getfloat("end_x")
    end_y = coor_conf.getfloat("end_y")

    return start_x, start_y, end_x, end_y


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
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext in (".arw", ".raw"):
        image = open_raw_image(path)
    else:
        image = Image.open(path)

    return image


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


if __name__ == "__main__":
    MASTER = tk.Tk()
    APP = BatchCropper(MASTER)
    APP.master.title("batch_crop")  # type: ignore
    MASTER.mainloop()
