========
Usage
========

.. _WTForms: https://wtforms.readthedocs.org/
.. _wtforms.Form: https://wtforms.readthedocs.org/en/latest/forms.html
.. _wtforms.Field: https://wtforms.readthedocs.org/en/latest/fields.html

This documentation assumes that you're somewhat familiar with `WTForms`_,
since Minform is intentionally similar to (and substantively derived from)
that project.

Minform provides a :class:`BinaryForm <minform.BinaryForm>` class, which
subclasses from `wtforms.Form`_. Instead of subclassing ``wtforms.Form`` with
`wtforms.Field`_ instances as class variables, you need to subclass
:class:`BinaryForm <minform.BinaryForm>`, and give it :class:`BinaryItem
<minform.BinaryItem>` instances as class variables. The result will be a
``Form`` with additional :meth:`pack <minform.BinaryForm.pack>` and
:meth:`unpack <minform.BinaryForm.unpack>` methods.

Base Classes
------------

.. autoclass:: minform.BinaryForm
    :members:

.. autoclass:: minform.BinaryItem

    A number of :class:`BinaryItem <minform.BinaryItem>` subclasses have
    already been provided; see :ref:`items` for more.

    :members:

    .. attribute:: size

        The number of bytes that will be used to store the item when the
        parent form is packed in a buffer.

    .. note::

        If you subclass :class:`BinaryItem <minform.BinaryItem>`, you need to
        ensure that the object will have an appropriate :attr:`size <.>`
        property, since it is used by the form to split up buffer data for
        unpacking, and to assembled packed data.

    .. attribute:: form_field

        This property is optional; for example, :class:`BlankBytes
        <minform.BlankBytes>` instances do not have a :attr:`form_field <.>`.
        If present, it should be an instance of `wtforms.Field
        <https://wtforms.readthedocs.org/en/latest/fields.html>`_. This field
        will then become a member of the form, just like a field in a
        ``wtforms.Form``.


Binary Items
------------

Blank Bytes
~~~~~~~~~~~

.. autoclass:: minform.BlankBytes

Binary Fields
~~~~~~~~~~~~~

.. class:: minform.BinaryField(label='', validators=None, order=None, **kwargs)

    .. note::

        This class should not be instantiated directly. Instead, use one of
        its subclasses, described below.

    The following classes all have :attr:`form_field <BinaryItem.form_field>`
    attributes, and their constructors accept a superset of the construction
    parameters for a `wtforms.Field`_. In general, constructor arguments whose
    names correspond to :class:`BinaryItem <minform.BinaryItem>` construction
    parameters will be passed in to the constructor for the corresponding
    ``wtforms.Field``. So, for example, you can set a ``label`` for HTML
    rendering, or add extra ``validators``.

    The only notable exceptions are the ``order`` and ``length`` parameters,
    which are used to set the :ref:`byte order <byte-order>` and :ref:`length
    policy <length>`, and will not be passed through to the ``Field``.

.. autoclass:: minform.BinaryBooleanField(BinaryField arguments)
.. autoclass:: minform.CharField(BinaryField arguments)
.. autoclass:: minform.basic.BinaryIntegerField(BinaryField arguments)
.. autoclass:: minform.Float32Field(BinaryField arguments)
.. autoclass:: minform.Float64Field(BinaryField arguments)
.. autoclass:: minform.BytesField(BinaryField arguments, length=minform.AUTOMATIC)

.. autoclass:: minform.BinaryFieldList(inner_field, BinaryField arguments, max_entries=None, length=minform.EXPLICIT)
    :members:

.. autoclass:: minform.BinaryFormField(form_class, BinaryField arguments)
    :members:

Custom BinaryItems
~~~~~~~~~~~~~~~~~~

When creating a custom :class:`BinaryItem <minform.BinaryItem>`, you need to
be sure to include:

* A ``size`` attribute. This is used to determine how many bytes will be
  required by the ``unpack`` method, and how many will be expected to be
  returned by the ``pack`` method. This attribute is required even if you
  write custom ``pack`` and ``unpack`` methods that don't refer to it!

* A ``pack(self, data, order=None)`` method. The type of ``data`` should be
  compatible with the type returned by the ``unpack`` method (below).

* An ``unpack(self, buf, order=None)`` method. You can expect ``buf`` to have
  ``self.size`` bytes when the method is invoked in the course of using a
  ``BinaryForm``.

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

        If the length is :data:`FIXED <.>`, all of the packed information, including terminal null bytes, will be considered part of the data.::

            fixed_bytes = BytesField(max_length=6, length=FIXED)
            fixed_bytes.unpack(b'foobar\0\0\0\0') == b'foobar\0\0\0\0'

            fixed_list = BinaryFieldList(UInt16Field(), max_entries=4, length=FIXED)
            fixed_list.unpack(b'\x12\x34\x56\x78\x9a\x00\x00\x00') == [0x1234, 0x5678, 0x9a00, 0x0000]

    .. autodata:: EXPLICIT
        :annotation:

        If length is :data:`EXPLICIT <.>`, the packed buffer will start with
        an unsigned int that gives the length of the data (the number of bytes
        in a :class:`BytesField <minform.BytesField>`, or the number of
        entries in a :class:`BinaryFieldList <minform.BinaryFieldList>`). This
        prefix will be sized according to necessity; it will always be big
        enough to store the ``max_length`` or ``max_entries`` of the field:

        ================== =========== ===========
        maximum            prefix type prefix size
        ================== =========== ===========
        up to 255          UInt8       1 byte
        256 - 65535        UInt16      2 bytes
        65535 - 4294967296 UInt32      4 bytes
        larger             UInt64      8 bytes
        ================== =========== ===========

        If the max is larger than 2\ :sup:`64`, a ``ValueError`` will be
        thrown. Here are some examples of the use of :data:`EXPLICIT <.>`
        length fields:::

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

        The :data:`AUTOMATIC <.>` option is only available for
        :class:`BytesField <minform.BytesField>`, and has very simple
        semantics: strings shorter than ``max_length`` will be padded with
        null bytes when packed, and null bytes will be trimmed from the end
        when unpacking a buffer.::

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
    order-size-and-alignment>`_. The :data:`minform.NATIVE` constant
    corresponds to the ``'='`` prefix, rather than ``'@'``.

.. note::

    Setting the ``order`` property on a :class:`BinaryForm
    <minform.BinaryForm>` or :class:`BinaryItem <minform.BinaryItem>` will
    override the ``order`` argument of :meth:`pack <minform.BinaryItem.pack>`
    and :meth:`unpack <minform.BinaryItem.unpack>` methods. For clarity, we
    recommend that you use **either** the attribute **or** the :meth:`pack
    <minform.BinaryItem.pack>`/:meth:`unpack <minform.BinaryItem.unpack>`
    argument.
