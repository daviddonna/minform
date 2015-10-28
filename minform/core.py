import abc
import six
import wtforms

__all__ = [
    'FIXED', 'AUTOMATIC', 'EXPLICIT',
    'NATIVE', 'LITTLE_ENDIAN', 'BIG_ENDIAN', 'NETWORK',
    'BinaryItem', 'BlankBytes', 'BinaryField', 'BinaryForm',
]

FIXED = 'fixed'
AUTOMATIC = 'automatic'
EXPLICIT = 'explicit'

NATIVE = '='
LITTLE_ENDIAN = '<'
BIG_ENDIAN = '>'
NETWORK = '!'

_creation_id = 0


def _new_creation_id():
    global _creation_id
    _creation_id += 1
    return _creation_id


class BinaryItem(six.with_metaclass(abc.ABCMeta, object)):

    """
    Item that occupies a block of bytes in a :class:`BinaryForm
    <minform.BinaryForm>`
    """

    order = None
    form_field = None

    def __init__(self):
        self._creation_id = _new_creation_id()

    @abc.abstractmethod
    def pack(self, data, order=None):
        """
        Serialize a chunk of data into packed bytes.

        :param data: to serialize, e.g. stored by a corresponding form field
        :param order: :ref:`byte order <byte-order>` constant dictating the
            endianness of packed integers. *If* ``self.order`` *is set, this
            parameter will be ignored.*
        :return: bytes object with length ``self.size``
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def unpack(self, buf, order=None):
        """
        :param buf: bytes object of length ``self.size``
        :param order: :ref:`byte order <byte-order>` constant for integer
            endianness. *If* ``self.order`` *is set, this parameter will be
            ignored.*
        :return: data stored in the buffer
        :raises: ``ValueError`` if ``buf`` has the wrong size.
        """
        pass  # pragma: no cover

    def pack_into(self, buffer, offset, data, order=None):
        if len(buffer[offset:offset+self.size]) < self.size:
            raise ValueError("Need at least {0} bytes to pack {1}".format(
                self.size, data))
        buffer[offset:offset+self.size] = self.pack(data, order=order)

    def unpack_from(self, buffer, offset=0, order=None):
        if offset == -self.size:
            buf = buffer[offset:]
        else:
            buf = buffer[offset:offset+self.size]
        if len(buf) < self.size:
            raise ValueError("{0} is too small for a {1}".format(
                buf, self.__class__.__name__))
        return self.unpack(buf, order=order)


class BlankBytes(BinaryItem):

    """
    Add padding to a form when serialized.

    A :class:`BlankBytes <.>` instance can be placed anywhere in the list of
    fields in a :class:`BinaryForm <minform.BinaryForm>` definition. It
    doesn't matter what name you give it; when the form's fields are
    processed, the :class:`BlankBytes <.>` object itself will be removed from
    the class's namespace.

    The corresponding bytes will be null when the form is packed, and ignored
    when a data buffer is unpacked. Likewise, the bytes in a packed buffer
    will be ignored, and unpacking blank bytes will always return ``None``.

    Because :class:`BlankBytes <.>` objects lack a :attr:`form_field
    <minform.BinaryItem.form_field>` attribute, there will be no corresponding
    attribute in a parent :class:`BinaryForm <minform.BinaryForm>`'s data.
    """

    name = None

    def __init__(self, size):
        """
        The :class:`BlankBytes <.>` item will correspond to ``size`` packed
        bytes.
        """

        super(BlankBytes, self).__init__()
        self.size = size

    def pack(self, data, order=None):
        return b'\0' * self.size

    def unpack(self, buf, order=None):
        return None


class BinaryField(BinaryItem):

    pass


class BinaryFormMeta(wtforms.Form.__class__):

    def __new__(cls, name, bases, nmspc):
        binary_items = []

        # We need to construct a list because the .items() iterator will throw
        # a RuntimeError if the size of nmspc changes during the loop.
        for key, value in list(nmspc.items()):
            if isinstance(value, BinaryItem):
                binary_items.append(value)
                value.name = key
                if value.form_field is not None:
                    nmspc[key] = value.form_field
                else:
                    del nmspc[key]
        binary_items.sort(key=lambda item: item._creation_id)
        nmspc['_binary_items'] = binary_items
        nmspc['size'] = sum(item.size for item in binary_items)
        return super(BinaryFormMeta, cls).__new__(cls, name, bases, nmspc)


class BinaryForm(six.with_metaclass(BinaryFormMeta, wtforms.Form)):

    """
    Form with the power to serialize to and deserialize from packed bytes!

    A :class:`BinaryForm <.>` is used much like a `wtforms.Form
    <https://wtforms.readthedocs.org/en/latest/forms.html>`_. Instead of
    `wtforms.Field <https://wtforms.readthedocs.org/en/latest/fields.html>`_
    instances, however, the class members should be instances of
    :class:`BinaryItem <minform.BinaryItem>`.

    When the class is created, the :class:`BinaryItem <minform.BinaryItem>`
    class members will be used, in order, to generate a binary protocol for
    serializing and deserializing instances of the form. Using the
    :class:`BinaryForm <.>` subclass's :meth:`unpack
    <minform.BinaryForm.unpack>` method will bind a form to the data
    represented by a buffer.

    .. attribute:: size

        The number of bytes in a packed buffer of data for this class.

    .. attribute:: order

        Byte ordering of numbers, etc. in corresponding buffers of packed
        data. See :ref:`Byte Order <byte-order>` for more.
    """

    order = None

    @classmethod
    def unpack(cls, buf, order=None):
        """
        ``cls`` is the class on which this method is being called.

        :param buf: bytes object of length ``cls.size``
        :param order: :ref:`byte order <byte-order>` constant for integer
            endianness. *If* ``cls.order`` *is set, this parameter will be
            ignored.*
        :return: instance of ``cls`` bound to the data stored in the buffer
        :raises: ``ValueError`` if ``buf`` has the wrong size.
        """

        if len(buf) != cls.size:
            raise ValueError('Recieved {0} bytes; expected {1}'.format(
                len(buf), cls.size))
        order = order or cls.order or ''
        data = {}
        start = 0

        for item in cls._binary_items:
            stop = start + item.size
            if item.form_field is not None:
                data[item.name] = item.unpack(buf[start:stop], order=order)
            else:
                item.unpack(buf[start:stop])
            start = stop

        return cls(data=data)

    def pack(self, order=None):
        """
        Serialize this form's bound data into packed bytes.

        :param order: :ref:`byte order <byte-order>` constant dictating the
            endianness of packed integers. *If* ``self.order`` *is set, this
            parameter will be ignored.*
        :return: bytes object with length ``self.size``
        """

        order = order or self.order or ''

        size = sum(item.size for item in self._binary_items)
        buf = bytearray(size)
        start = 0

        for item in self._binary_items:
            stop = start + item.size
            if item.form_field is not None:
                value = self.data[item.name]
                buf[start:stop] = item.pack(value, order=order)
            else:
                buf[start:stop] = item.pack(None)
            start = stop

        return bytes(buf)

    def pack_into(self, buffer, offset, order=None):
        if len(buffer[offset:offset+self.size]) < self.size:
            raise ValueError("Need at least {0} bytes to pack {1}".format(
                self.size, self.data))
        buffer[offset:offset+self.size] = self.pack(order=order)

    @classmethod
    def unpack_from(cls, buffer, offset=0, order=None):
        if offset == -cls.size:
            buf = buffer[offset:]
        else:
            buf = buffer[offset:offset+cls.size]
        if len(buf) < cls.size:
            raise ValueError("{0} is too small for a {1}".format(
                buf, cls.__name__))
        return cls.unpack(buf, order=order)
