API
===

Base Classes
------------

.. autoclass:: minform.BinaryForm
    :members:

.. autoclass:: minform.BinaryItem
    :members:

Items
-----

.. autoclass:: minform.BlankBytes
    :members:

Custom BinaryItems
~~~~~~~~~~~~~~~~~~

Length
------

.. _length:

.. automodule:: minform

    The following constants are used as the ``length`` argument when
    constructing a :class:`BytesField <minform.basic.BytesField>` or a
    :class:`BinaryFieldList <minform.compound.BinaryFieldList>`; they control
    whether and how the packed buffer signals the length of the data.

    .. autodata:: FIXED
        :annotation:

        If the length is ``FIXED``, all of the packed information, including terminal null bytes, will be considered part of the data.::

            fixed_bytes = BytesField(max_length=6, length=FIXED)
            fixed_bytes.unpack(b'foobar\0\0\0\0') == b'foobar\0\0\0\0'

            fixed_list = BinaryFieldList(UInt16Field(), max_entries=4, length=FIXED)
            fixed_list.unpack(b'\x12\x34\x56\x78\x9a\x00\x00\x00') == [0x1234, 0x5678, 0x9a00, 0x0000]

    .. autodata:: EXPLICIT
        :annotation:

        If length is ``EXPLICIT``, the packed buffer will start with an
        unsigned int that gives the length of the data (the number of bytes in
        a ``BytesField``, or the number of entries in a ``BinaryFieldList``).
        This prefix will be sized according to necessity; it will always be
        big enough to store the ``max_length`` or ``max_entries`` of the
        field:

        ================== =========== ===========
        maximum            prefix type prefix size
        ================== =========== ===========
        up to 255          UInt8       1 byte
        256 - 65535        UInt16      2 bytes
        65535 - 4294967296 UInt32      4 bytes
        larger             UInt64      8 bytes
        ================== =========== ===========

        If the max is larger than 2\ :sup:`64`, a ``ValueError`` will be thrown.
        Here are some examples of the use of ``EXPLICIT`` length fields:::

            explicit_bytes = BytesField(max_length=9, length=EXPLICIT)

            # The first byte is the length of the string.
            explicit_bytes.pack(b'foobar') == b'\x06foobar\0\0\0'

            # If you manually include the null bytes, they'll be preserved.
            explicit_bytes.pack(b'foo\0\0\0') == b'\x06foo\0\0\0\0\0\0'

            # The unpacking process respects the explicit size given.
            explicit_bytes.unpack(b'\x05hey\0\0\0\0\0\0') == b'hey\0\0'
            explicit_bytes.unpack(b'\x02hey\0\0\0\0\0\0') == b'he'

            explicit_list = BinaryFieldList(UInt16Field, max_entries=4, length=EXPLICIT)

            explicit_list.pack([0x1234, 0x5678, 0x9abc, 0xdef0]) == b'\x04\x12\x34\x56\x78\x9a\xbc\xde\xf0'
            explicit_list.pack([0x1234, 0x5678]) == b'\x02\x12\x34\x56\x78\0\0\0\0'

    .. autodata:: AUTOMATIC
        :annotation:

        The ``AUTOMATIC`` option is only available for ``BytesField``\ s, and has
        very simple semantics: strings shorter than ``max_length`` will be
        padded with null bytes when packed, and null bytes will be trimmed
        from the end when unpacking a buffer.::

            auto_bytes = BytesField(max_length=10, length=AUTOMATIC)

            auto_bytes.pack(b'1234554321') == b'1234554321'
            auto_bytes.pack(b'foobar') == b'foobar\0\0\0\0'

            auto_bytes.unpack(b'abc\0def\0\0\0') == b'abc\0def'

Byte order
----------

.. _byte-order:

.. autodata:: NATIVE
    :annotation:
.. autodata:: LITTLE_ENDIAN
    :annotation:
.. autodata:: BIG_ENDIAN
    :annotation:
.. autodata:: NETWORK
    :annotation:

    These constants operate according to the `byte order constants from
    the struct module <https://docs.python.org/3/library/struct.html#byte-
    order-size-and-alignment>`_. The ``minform.NATIVE`` constant
    corresponds to the ``'='`` prefix, rather than ``'@'``.

.. note::

    Setting the ``order`` property on a ``BinaryForm`` or ``BinaryItem`` will
    override the ``order`` argument of ``pack`` and ``unpack`` methods. For clarity, we recommend that you use **either** the attribute **or** the ``pack``/``unpack`` argument.
