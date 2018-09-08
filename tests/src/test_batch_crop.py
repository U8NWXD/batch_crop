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

# pylint: disable=missing-docstring


from math import isclose

from hypothesis import given, assume
import hypothesis.strategies as st

from batch_crop.batch_crop import coor_to_box, coors_to_ratios, \
    ratios_to_coors, gen_ratios_config, get_ratios_from_config, open_image


TEST_RES = "tests/res/"


@given(st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False))
def test_coor_to_box(x1: float, y1: float, x2: float, y2: float):
    box_coor = x1, y1, x2, y2
    box = coor_to_box(box_coor)
    left, upper, right, lower = box

    assert left <= right
    assert upper <= lower
    assert list(box_coor).sort() == list(box).sort()


@given(st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False))
def test_coors_to_ratios(width: float,  # pylint: disable=too-many-arguments
                         height: float,
                         x1: float, y1: float, x2: float, y2: float):
    image_size = width, height
    coors = x1, y1, x2, y2
    box_ratio = coors_to_ratios(image_size, coors)
    r_x1, r_y1, r_x2, r_y2 = box_ratio

    assert r_x1 == x1 / width
    assert r_x2 == x2 / width
    assert r_y1 == y1 / height
    assert r_y2 == y2 / height


@given(st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False))
def test_ratios_to_coors(width: float,  # pylint: disable=too-many-arguments
                         height: float,
                         x1: float, y1: float, x2: float, y2: float):
    image_size = width, height
    box_ratio = x1, y1, x2, y2
    box_coors = ratios_to_coors(image_size, box_ratio)
    c_x1, c_y1, c_x2, c_y2 = box_coors

    assert c_x1 == x1 * width
    assert c_x2 == x2 * width
    assert c_y1 == y1 * height
    assert c_y2 == y2 * height


@given(st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False))
def test_ratios_coors_interconversion(  # pylint: disable=too-many-arguments
        width: float, height: float,
        x1: float, y1: float, x2: float, y2: float):
    image_size = width, height
    box = x1, y1, x2, y2

    out = coors_to_ratios(image_size, ratios_to_coors(image_size, box))
    assume(float("inf") not in out)
    for box_val, out_val in zip(box, out):
        assert isclose(box_val, out_val)


@given(st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False),
       st.floats(min_value=0.001, allow_nan=False, allow_infinity=False))
def test_coors_ratios_interconversion(  # pylint: disable=too-many-arguments
        width: float, height: float,
        x1: float, y1: float, x2: float, y2: float):
    image_size = width, height
    box = x1, y1, x2, y2

    out = ratios_to_coors(image_size, coors_to_ratios(image_size, box))
    assume(float("inf") not in out)
    for box_val, out_val in zip(box, out):
        assert isclose(box_val, out_val)


@given(st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False),
       st.floats(allow_nan=False, allow_infinity=False))
def test_ratios_config_interconversion(x1: float, y1: float,
                                       x2: float, y2: float):
    box_ratio = x1, y1, x2, y2
    out = get_ratios_from_config(gen_ratios_config(box_ratio))

    assert box_ratio == out


def test_open_image():
    open_image(TEST_RES + "image.JPG")
