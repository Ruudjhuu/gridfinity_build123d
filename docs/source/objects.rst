Objects
=======

This page lists some of the objects you can create with the gridfinity_build123d library. Due to the modularity it is impossible to list everything. Don't let these examples be the end of your imagination.

Bins
----

.. currentmodule:: gridfinity_build123d.bin

.. testsetup:: *

    from gridfinity_build123d import *

.. grid:: 2

    .. grid-item-card:: :class:`Bin`

        .. raw:: html

            <details>
            <summary>source</summary>

        .. testcode::

            Bin(
                Base(), height_in_units=4,
            )

        .. raw:: html

            </details>

        .. image:: ../assets/bin.png

    .. grid-item-card:: :class:`CompartmentsEqual`

        .. raw:: html

            <details>
            <summary>source</summary>

        .. testcode::

            Bin(
                Base(),
                height_in_units=4,
                compartments=CompartmentsEqual(
                    div_x=2,
                    compartment_list=Compartment(Label()),
                ),
            )

        .. raw:: html

            </details>

        .. image:: ../assets/bin_compartment.png

    .. grid-item-card:: :class:`StackingLip`

        .. raw:: html

            <details>
            <summary>source</summary>

        .. testcode::

            Bin(
                Base(),
                height_in_units=4,
                compartments=CompartmentsEqual(
                    div_x=2,
                    compartment_list=Compartment(Label()),
                ),
                lip=StackingLip(),
            ),

        .. raw:: html

            </details>

        .. image:: ../assets/bin_lip.png


BasePlates
----------

.. currentmodule:: gridfinity_build123d.baseplate


.. grid:: 2

    .. grid-item-card:: :class:`BasePlateEqual`

        .. raw:: html

            <details>
            <summary>source</summary>

        .. testcode::

            BasePlateEqual(
                size_x=2,
                size_y=2,
            )

        .. raw:: html

            </details>

        .. image:: ../assets/base_plate_equal.png


    .. grid-item-card:: :class:`BasePlate`

        .. raw:: html

            <details>
            <summary>source</summary>

        .. testcode::

            BasePlate([[True,True],[True]])

        .. raw:: html

            </details>

        .. image:: ../assets/base_plate.png

    .. grid-item-card:: :class:`BasePlateBlockFull`

        .. raw:: html

            <details>
            <summary>source</summary>

        .. testcode::

            BasePlateEqual(
                size_x=2,
                size_y=2,
                baseplate_block=BasePlateBlockFull(),
            )

        .. raw:: html

            </details>

        .. image:: ../assets/base_plate_full.png

    .. grid-item-card:: :class:`BasePlateBlockFull`

        .. raw:: html

            <details>
            <summary>source</summary>

        .. testcode::

            BasePlateEqual(
                size_x=2,
                size_y=2,
                baseplate_block=BasePlateBlockFull(),
            )

        .. raw:: html

            </details>

        .. image:: ../assets/base_plate_weigthed.png


Bases
-----
.. currentmodule:: gridfinity_build123d.base

.. grid:: 2

    .. grid-item-card:: :class:`BaseEqual`

        .. raw:: html

            <details>
            <summary>source</summary>

        .. testcode::

            BaseEqual(
                grid_x=2,
                grid_y=2,
            )

        .. raw:: html

            </details>

        .. image:: ../assets/base_equal.png

    .. grid-item-card:: :class:`Base`

        .. raw:: html

            <details>
            <summary>source</summary>

        .. testcode::

            Base([[True,True],[True]])

        .. raw:: html

            </details>

        .. image:: ../assets/base.png


    .. grid-item-card:: :class:`BaseBlock`

        .. raw:: html

            <details>
            <summary>source</summary>

        .. testcode::

            BaseEqual(2, 2, [MagnetHole(
                BottomCorners()),
                ScrewHole(BottomCorners(),
                )])

        .. raw:: html

            </details>

        .. image:: ../assets/base_holes.png
