import struct
import wtforms
from wtforms.validators import Length, NumberRange

from . import core


class BasicBinaryField(core.BinaryField):

    # Some BinaryFields will have inherent value restrictions, based on the
    # limitations of the serialized form. For example, a UInt8Field cannot
    # store numbers above 0xFF. When the class is instantiated, these
    # validators will be silently added to any validators provided by the
    # constructor.
    initial_validators = []

    def __init__(self, label='', validators=None, order=None, **kwargs):
        core.BinaryItem.__init__(self)
        self.size = struct.calcsize(self.pack_string)
        self.order = order

        # Clone the initial_validators list to avoid mutating a class
        # variable.
        all_vldtrs = list(self.initial_validators)
        if validators is not None:
            all_vldtrs.extend(validators)

        self.form_field = self.form_field_class(label, all_vldtrs, **kwargs)

    def pack(self, data, order=None):
        order = self.order or order or ''
        return self.pack_data(data, order)

    def pack_data(self, data, order):
        return struct.pack(order + self.pack_string, data)

    def unpack(self, buffer, order=None):
        order = self.order or order or ''
        return self.unpack_data(buffer, order)

    def unpack_data(self, buffer, order):
        return struct.unpack(order + self.pack_string, buffer)[0]


class CharField(BasicBinaryField):

    """
    Store a single byte as a one-character ``str`` (in Python 2) or ``bytes``
    object (in Python 3).

    Attributes:
        size: always ``1``
        form_field: A :class:`wtforms.fields.StringField` instance.
    """

    form_field_class = wtforms.StringField
    initial_validators = [Length(min=1, max=1)]
    pack_string = 'c'


class BinaryBooleanField(BasicBinaryField):

    """
    Store either ``True`` or ``False`` as ``b'\\x01'`` or ``b'\\x00'``
    (respectively).

    Attributes:
        size: always ``1``
        form_field: A :class:`wtforms.fields.BooleanField` instance.
    """

    form_field_class = wtforms.BooleanField
    pack_string = '?'


class BinaryIntegerField(BasicBinaryField):

    """
    This class should not be instantiated directly; instead, you should use
    one of its subclasses, which determine what kind of int is stored, and
    how. Those subclasses are:

    ==================== ==== =============== ================
    Name                 size Min             Max
    ==================== ==== =============== ================
    :class:`Int8Field`   1    -128            127
    :class:`UInt8Field`  1    0               255
    :class:`Int16Field`  2    -32768          32767
    :class:`UInt16Field` 2    0               65535
    :class:`Int32Field`  4    -2\ :sup:`31`   2\ :sup:`31` - 1
    :class:`UInt32Field` 4    0               2\ :sup:`32` - 1
    :class:`Int64Field`  8    -2\ :sup:`63`   2\ :sup:`63` - 1
    :class:`UInt64Field` 8    0               2\ :sup:`64` - 1
    ==================== ==== =============== ================

    Attributes:
        form_field: A :class:`wtforms.fields.Integerfield` instance.
    """

    form_field_class = wtforms.IntegerField

    @property
    def initial_validators(self):
        return [NumberRange(self.min, self.max)]


class Int8Field(BinaryIntegerField):

    pack_string = 'b'
    min = -128
    max = 127


class UInt8Field(BinaryIntegerField):

    pack_string = 'B'
    min = 0
    max = (2 ** 8) - 1


class Int16Field(BinaryIntegerField):

    pack_string = 'h'
    min = -(2 ** 15)
    max = (2 ** 15) - 1


class UInt16Field(BinaryIntegerField):

    pack_string = 'H'
    min = 0
    max = (2 ** 16) - 1


class Int32Field(BinaryIntegerField):

    pack_string = 'i'
    min = -(2 ** 31)
    max = (2 ** 31) - 1


class UInt32Field(BinaryIntegerField):

    pack_string = 'I'
    min = 0
    max = (2 ** 32) - 1


class Int64Field(BinaryIntegerField):

    pack_string = 'q'
    min = -(2 ** 63)
    max = (2 ** 63) - 1


class UInt64Field(BinaryIntegerField):

    pack_string = 'Q'
    min = 0
    max = (2 ** 64) - 1


class Float32Field(BasicBinaryField):

    """
    Store a ``float`` in four bytes.

    Attributes:
        size: Always ``4``.
        form_field: A :class:`wtforms.fields.FloatField` instance.
    """

    form_field_class = wtforms.FloatField
    pack_string = 'f'


class Float64Field(BasicBinaryField):

    """
    Store a ``float`` in eight bytes.

    Attributes:
        size: Always ``8``.
        form_field: A :class:`wtforms.fields.FloatField` instance.
    """

    form_field_class = wtforms.FloatField
    pack_string = 'd'


class BytesField(BasicBinaryField):

    """
    Store *N* bytes.

    Attributes:
        max_length: Maximum number of bytes in the stored string. Note that
            this may not be equal to :attr:`size`.

        size: The :attr:`size` of a :class:`BytesField` with ``max_length``
            *N* varies based on the *length* argument used to construct it.

            If *length* is :attr:`~minform.FIXED` or
            :attr:`~minform.AUTOMATIC`, ``size`` will be *N*.

            If *length* is :attr:`~minform.EXPLICIT`, there will be one or
            more extra bytes at the beginning of the packed data, which store
            the number of bytes used by the string. This will be the smallest
            number of bytes needed to store a number up to ``max_length``. So,
            ``size`` can be *N+1*, *N+2*, *N+4*, or *N+8*. (For more
            information, see the documentation for :data:`~minform.EXPLICIT`.)

        form_field: A :class:`wtforms.fields.StringField` instance.
    """

    form_field_class = wtforms.StringField

    def __init__(self, label='', validators=None, max_length=None,
                 length=core.AUTOMATIC, order=None, **kwargs):

        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError('BytesField must be created with a '
                             'positive max_length keyword argument.')

        self.order = order
        self.length = length

        self.max_length = max_length

        if self.length == core.FIXED:
            self.initial_validators = [Length(max=max_length, min=max_length)]
            self.pack_string = '{0}s'.format(max_length)

        elif self.length == core.AUTOMATIC:
            self.initial_validators = [Length(max=max_length)]
            self.pack_string = '{0}s'.format(max_length)

        elif self.length == core.EXPLICIT:
            self.initial_validators = [Length(max=max_length)]
            self.length_field = store_numbers_up_to(max_length, order=order)
            self.pack_string = '{0}{1}s'.format(self.length_field.pack_string,
                                                max_length)

        super(BytesField, self).__init__(label, validators, order, **kwargs)

    def pack_data(self, data, order):
        buffer = bytearray(self.size)
        length = len(data)
        if self.length == core.EXPLICIT:
            pack_length_string = order + self.length_field.pack_string
            struct.pack_into(pack_length_string, buffer, 0, length)
            start = self.length_field.size
        else:
            start = 0
        buffer[start:start+length] = data
        return buffer

    def unpack_data(self, buffer, order):
        if self.length == core.EXPLICIT:
            unpack_length_string = order + self.length_field.pack_string
            length = struct.unpack_from(unpack_length_string, buffer)[0]
            if length > self.max_length:
                message = "Buffer cannot contain {0} bytes.".format(length)
                raise ValueError(message)
            data_buffer = buffer[self.length_field.size:]
        else:
            length = self.max_length
            data_buffer = buffer
        data = data_buffer[:length]

        if self.length == core.AUTOMATIC:
            data = data.rstrip(b'\x00')

        return data


def store_numbers_up_to(n, signed=False, **kwargs):
    """
    Return a BinaryField class that can store numbers up to a certain maximum.

    If the number is too big to store, a ``ValueError`` will be raised.

    Parameters:
        n: The highest number that you expect to need to store (must be at
            most a 64-bit integer).
        signed: Return a field that can store negative numbers.
        kwargs: Additional arguments get passed into the binary field
            constructor.

    Returns:
        BinaryIntegerField: A :class:`BinaryIntegerField` that can store
            numbers up to at least ``n``.
    """

    if signed:
        if n <= Int8Field.max:
            return Int8Field(**kwargs)
        elif n <= Int16Field.max:
            return Int16Field(**kwargs)
        elif n <= Int32Field.max:
            return Int32Field(**kwargs)
        elif n <= Int64Field.max:
            return Int64Field(**kwargs)
        else:
            raise ValueError("Can't track numbers up to {0}".format(n))
    else:
        if n <= UInt8Field.max:
            return UInt8Field(**kwargs)
        elif n <= UInt16Field.max:
            return UInt16Field(**kwargs)
        elif n <= UInt32Field.max:
            return UInt32Field(**kwargs)
        elif n <= UInt64Field.max:
            return UInt64Field(**kwargs)
        else:
            raise ValueError("Can't track numbers up to {0}".format(n))
