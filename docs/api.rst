========
API
========

.. _WTForms: https://wtforms.readthedocs.org/

.. automodule:: minform

    This documentation assumes that you're somewhat familiar with `WTForms`_,
    since Minform is intentionally similar to (and substantively derived from)
    that project.

    Minform provides a :class:`BinaryForm` class, which subclasses from
    :class:`wtforms.Form <wtforms.form.Form>`. Instead of subclassing
    :class:`~wtforms.form.Form` with :class:`wtforms.Field
    <wtforms.fields.Field>` instances as class variables, you need to subclass
    :class:`BinaryForm`, and give it :class:`BinaryItem` instances as class
    variables. The result will be a :class:`~wtforms.form.Form` with
    additional :meth:`~BinaryForm.pack` and :meth:`~BinaryForm.unpack`
    methods.

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

Binary Fields
~~~~~~~~~~~~~

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
    .. autoclass:: BinaryFieldList
        :members: size form_field
    .. autoclass:: BinaryFormField
        :members: size form_field

Custom BinaryItems
~~~~~~~~~~~~~~~~~~

    When creating a custom :class:`BinaryItem`, you need to be sure to
    include:

    * A :attr:`~BinaryItem.size` attribute. This is used to determine how many
      bytes will be required by the ``unpack`` method, and how many will be
      expected to be returned by the ``pack`` method. This attribute is
      required even if you write custom ``pack`` and ``unpack`` methods that
      don't refer to it!

    * A :meth:`~BinaryItem.pack` method. The type of :paramref:`~minform.BinaryItem.pack.data` should be compatible with the type returned by the :meth:`~BinaryItem.unpack` method (below).

    * An :meth:`~BinaryItem.unpack` method. You can expect :paramref:`~minform.BinaryItem.unpack.buf` to have ``self.size`` bytes when the method is
      invoked in the course of using a :class:`BinaryForm`.

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

    Setting the ``order`` property on a :class:`BinaryForm
    <minform.BinaryForm>` or :class:`BinaryItem <minform.BinaryItem>` will
    override the ``order`` argument of :meth:`pack <minform.BinaryItem.pack>`
    and :meth:`unpack <minform.BinaryItem.unpack>` methods. For clarity, we
    recommend that you use **either** the attribute **or** the :meth:`pack
    <minform.BinaryItem.pack>`/:meth:`unpack <minform.BinaryItem.unpack>`
    argument.
