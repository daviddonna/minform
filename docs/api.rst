========
API
========

.. _WTForms: https://wtforms.readthedocs.org/

.. automodule:: minform

    This documentation assumes that you're somewhat familiar with `WTForms`_,
    since Minform is intentionally similar to (and substantively derived from)
    that project.

    Minform provides a :class:`BinaryForm` class, which subclasses from
    :class:`wtforms.form.Form`. Instead of subclassing
    :class:`~wtforms.form.Form` with :class:`wtforms.fields.Field` instances
    as class variables, you need to subclass :class:`BinaryForm`, and give it
    :class:`BinaryItem` instances as class variables. The result will be a
    :class:`~wtforms.form.Form` with additional :meth:`~BinaryForm.pack` and
    :meth:`~BinaryForm.unpack` methods.

    .. note::

        This documentation will often refer to ``bytes`` objects. This mostly
        applies to Python 3; if you're using Python 2, you can read ``bytes``
        as ``str``.

        ============== ============== ===================
        Python version raw bytes type unicode string type
        ============== ============== ===================
        Python 2       ``str``        ``unicode``
        Python 3       ``bytes``      ``str``
        ============== ============== ===================

Base Classes
------------

    .. autoclass:: BinaryForm
        :members:
    .. autoclass:: BinaryItem
        :members:

.. _items:

Binary Items
------------

Blank Bytes
~~~~~~~~~~~

    .. autoclass:: BlankBytes
        :members:

Basic Binary Fields
~~~~~~~~~~~~~~~~~~~

    .. autoclass:: BinaryField
        :members: size form_field
    .. autoclass:: BinaryBooleanField
        :members: size form_field
    .. autoclass:: CharField
        :members: size form_field
    .. autoclass:: BinaryIntegerField
        :members: size form_field
    .. autoclass:: Float32Field
        :members: size form_field
    .. autoclass:: Float64Field
        :members: size form_field
    .. autoclass:: BytesField
        :members: size form_field

Compound Binary Fields
~~~~~~~~~~~~~~~~~~~~~~

    These fields allow data to be nested. If your data may include several
    items with the same type, you can use a :class:`BinaryFieldList` to
    manage them. If you want to re-use a set of items (or nest a more
    complicated data type in a :class:`BinaryFieldList`), you can use a
    :class:`BinaryFormField` to do so.

    .. autoclass:: BinaryFieldList
        :members: size form_field
    .. autoclass:: BinaryFormField
        :members: size form_field

Custom BinaryItems
~~~~~~~~~~~~~~~~~~

    When creating a custom :class:`BinaryItem`, you need to be sure to
    include:

    * A :attr:`~BinaryItem.size` attribute. This is used to determine how many
      bytes will be required by the :meth:`~BinaryItem.unpack` method, and how
      many will be expected to be returned by the :meth:`~BinaryItem.pack`
      method. This attribute is required even if you write custom
      :meth:`~BinaryItem.pack` and :meth:`BinaryItem.unpack` methods that
      don't refer to it!

    * A :meth:`~BinaryItem.pack` method. The type of
      :paramref:`~minform.BinaryItem.pack.data` should be compatible with the
      type returned by the :meth:`~BinaryItem.unpack` method (below).

    * An :meth:`~BinaryItem.unpack` method. You can expect
      :paramref:`~minform.BinaryItem.unpack.buf` to have
      :attr:`self.size <BinaryItem.size>` bytes when the method is invoked in
      the course of using a :class:`BinaryForm`.

.. _length:

Length
------

.. automodule:: minform

    The following constants are used as the *length* argument when
    constructing a :class:`~minform.BytesField` or a
    :class:`~minform.BinaryFieldList`; they control whether and how the packed
    buffer signals the length of the data.

    .. autodata:: FIXED
        :annotation:
    .. autodata:: EXPLICIT
        :annotation:
    .. autodata:: AUTOMATIC
        :annotation:

.. _byte-order:

Byte order
----------

    .. autodata:: NATIVE
        :annotation:
    .. autodata:: LITTLE_ENDIAN
        :annotation:
    .. autodata:: BIG_ENDIAN
        :annotation:
    .. autodata:: NETWORK
        :annotation:

    .. note::

        Setting the :attr:`~BinaryItem.order` property on a
        :class:`BinaryForm` or :class:`BinaryItem <minform.BinaryItem>` will
        override the *order* argument of :meth:`~minform.BinaryItem.pack` and
        :meth:`~minform.BinaryItem.unpack` methods. For clarity, we recommend
        that you use **either** the attribute **or** the
        :meth:`~minform.BinaryItem.pack`/:meth:`~minform.BinaryItem.unpack`
        argument.

        Likewise, the :attr:`~BinaryItem.order` of a :class:`BinaryItem` will
        override the :attr:`~BinaryItem.order` of the form or field that
        contains it.

        You can think of it as the order cascading down from the
        :paramref:`BinaryForm.unpack` *order* argument, through the class, to
        each of that form's items, and easy nested item, until it is
        overridden by an :attr:`~BinaryItem.order` attribute.
