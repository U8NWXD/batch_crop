====================
Description of Units
====================

------------------------
Specific to This Project
------------------------

Ratios
======

A ratio is expressed as a fraction of the appropriate dimension.
For example, an x-coordinate of ``30`` when the width is ``100`` is
expressed as a ratio as ``0.3``. This allows coordinates to be
transferred between images of varying dimensions.

A ``box_ratio`` is a Tuple of 4 floats that describes a rectangular region in
the following format:

.. code-block:: python

   (start_x, start_y, end_x, end_y)

Each value of the Tuple is a ratio as defined above. ``(start_x, start_y)``
defines the coordinates of one corner of the rectangle, and ``(end_x, end_y)``
defines the opposing corner.

Coordinates
===========

A coordinate is a pair of numbers of the form ``(x, y)`` that defines a
particular point on the image. The coordinate system, as is standard in computer
science, places ``(0,0)`` in the upper-left corner while ``x`` increases to the
right and ``y`` increases downward. Coordinates are "absolute", not relative to
the size of the image, so the point ``(5,5)`` is in the middle of a ``10 x 10``
image, but in the lower right of a ``5 x 5`` image.

A ``box_coor`` is a Tuple of 4 floats that describes a rectangular region in the
following format:

.. code-block:: python

   (start_x, start_y, end_x, end_y)

``(start_x, start_y)`` is a coordinate for one corner of the rectangle, while
``(end_x, end_y)`` is a coordinate of the opposing corner.

-------------------
From Other Packages
-------------------

Size
====

The size of an image is expressed as a Tuple of the following format:

.. code-block:: python

   (width, height)

