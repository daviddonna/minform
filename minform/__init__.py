# -*- coding: utf-8 -*-
# flake8: noqa

__author__ = 'David Donna'
__email__ = 'davidadonna@gmail.com'
__version__ = '0.1.2'

from .core import *
from .basic import *
from .compound import *

FIXED = FIXED
r"""
If the length is :data:`FIXED <.>`, all of the packed information,
including terminal null bytes, will be considered part of the data.

.. code-block:: python

    fixed_bytes = BytesField(max_length=6, length=FIXED)
    fixed_bytes.unpack(b'foobar\0\0\0\0') == b'foobar\0\0\0\0'

    fixed_list = BinaryFieldList(UInt16Field(), max_entries=4, length=FIXED)
    fixed_list.unpack(b'\x12\x34\x56\x78\x9a\x00\x00\x00') == \
        [0x1234, 0x5678, 0x9a00, 0x0000]
"""

EXPLICIT = EXPLICIT
r"""
If length is :data:`EXPLICIT`, the packed buffer will start with an
unsigned int that gives the length of the data (the number of bytes in
a :class:`~minform.BytesField`, or the number of entries in a
:class:`~minform.BinaryFieldList`). This prefix will be sized
according to necessity; it will always be big enough to store the
:attr:`~minform.BytesField.max_length` or
:attr:`~minform.BinaryFieldList.max_entries` of the field:

================== =========== ===========
maximum            prefix type prefix size
================== =========== ===========
up to 255          UInt8       1 byte
256 - 65535        UInt16      2 bytes
65535 - 4294967296 UInt32      4 bytes
larger             UInt64      8 bytes
================== =========== ===========

If the max is larger than 2\ :sup:`64`, a ``ValueError`` will be
thrown. Here are some examples of the use of :data:`EXPLICIT`
length fields:

.. code-block:: python

    explicit_bytes = BytesField(max_length=9, length=EXPLICIT)

    # The first byte is the length of the string.
    explicit_bytes.pack(b'foobar') == b'\x06foobar\0\0\0'

    # If you manually include the null bytes, they'll be preserved.
    explicit_bytes.pack(b'foo\0\0\0') == b'\x06foo\0\0\0\0\0\0'

    # The unpacking process respects the explicit size given.
    explicit_bytes.unpack(b'\x05hey\0\0\0\0\0\0') == b'hey\0\0'
    explicit_bytes.unpack(b'\x02hey\0\0\0\0\0\0') == b'he'

    explicit_list = BinaryFieldList(UInt16Field, max_entries=4,
                                    length=EXPLICIT)

    explicit_list.pack([0x1234, 0x5678, 0x9abc, 0xdef0]) == \
        b'\x04\x12\x34\x56\x78\x9a\xbc\xde\xf0'
    explicit_list.pack([0x1234, 0x5678]) == b'\x02\x12\x34\x56\x78\0\0\0\0'
"""

AUTOMATIC = AUTOMATIC
r"""
The :data:`AUTOMATIC` option is only available for
:class:`~minform.BytesField`, and has very simple semantics: strings
shorter than *max_length* will be padded with null bytes when packed,
and null bytes will be trimmed from the end when unpacking a buffer.

.. code-block:: python

    auto_bytes = BytesField(max_length=10, length=AUTOMATIC)

    auto_bytes.pack(b'1234554321') == b'1234554321'
    auto_bytes.pack(b'foobar') == b'foobar\0\0\0\0'

    auto_bytes.unpack(b'abc\0def\0\0\0') == b'abc\0def'
"""

NATIVE = NATIVE  #:
LITTLE_ENDIAN = LITTLE_ENDIAN  #:
BIG_ENDIAN = BIG_ENDIAN  #:
NETWORK = NETWORK
r"""
These constants operate according to the `byte order constants from
the struct module <https://docs.python.org/3/library/struct.html#byte-
order-size-and-alignment>`_. The :data:`minform.NATIVE` constant
corresponds to the ``'='`` prefix, rather than ``'@'``.
"""
