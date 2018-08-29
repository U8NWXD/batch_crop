# `batch_crop`

A Python utility for batch cropping images

[![GPL Licence](https://badges.frapsoft.com/os/gpl/gpl.png?v=103)](LICENSE.txt)

## Requirements
* Python 3.6
* Tkinter
* Rawpy
* Pillow
* Numpy
* Contents of `requirements.txt`

## Usage

`python batch_crop.py dir_path extension`

For example, consider a directory that looks like this:
```
images
├── img1.ARW
├── img2.ARW
└── notes.txt
```
(output from `tree`)

Running `python batch_crop.py images ARW` opens a window displaying either
`img1.ARW` or `img2.ARW`. You can then click-and-drag to draw a box on the
image. When happy with the selection, click `Crop All` to crop all images with
the `ARW` extension to the box drawn. This creates a directory that looks like 
this:

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