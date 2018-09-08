# `batch_crop`

A Python utility for batch cropping images

[![GPL Licence](https://badges.frapsoft.com/os/gpl/gpl.png?v=103)](LICENSE.txt)
[![Documentation Status](https://readthedocs.org/projects/batch-crop/badge/?version=latest)](https://batch-crop.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/U8NWXD/batch_crop.svg?branch=master)](https://travis-ci.com/U8NWXD/batch_crop)
[![codecov](https://codecov.io/gh/U8NWXD/batch_crop/branch/master/graph/badge.svg)](https://codecov.io/gh/U8NWXD/batch_crop)

## Requirements
* Python 3.6
* Rawpy
* Pillow

Once you have Python 3.6, you can load the other requirements by executing
`pip install -r requirements.txt`.

## Getting Started

To download the latest code, run 

`$ git clone https://github.com/U8NWXD/batch_crop`

Then, after satisfying the requirements, launch the application by running

`python batch_crop.py`

For example, consider a directory that looks like this:
```
images
├── img1.ARW
├── img2.ARW
└── notes.txt
```
(output from `tree`)

Running `python batch_crop.py` opens a window with a button to `Load Image`.
Clicking that and selecting either `img1.ARW` or `img2.ARW` loads the selected
image into the window. You can then click-and-drag to draw a box on the
image. When happy with the selection, click `Crop All Matching Images` to crop 
all images in the `images` directory with the `ARW` extension to the box drawn. 
This creates a directory that looks like this:

```
images
├── img1.ARW
├── img1.ARW_cropped.jpg
├── img2.ARW
├── img2.ARW_cropped.jpg
└── notes.txt
```

where `img1.ARW_cropped.jpg` and `img2.ARW_cropped.jpg` store cropped forms of
`img1.ARW` and `img2.ARW` respectively.

## Contributing and Developer Documentation

Developer documentation is hosted at [readthedocs](https://readthedocs.io) at
this link: https://batch-crop.readthedocs.io/en/latest/

## Legal
Copyright (c) 2018  U8N WXD <cs.temporary@icloud.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.