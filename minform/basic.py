import struct
import wtforms
from wtforms.validators import Length, NumberRange

from . import core

__all__ = [
    'CharField', 'BytesField',
    'BinaryBooleanField',
    'Int8Field', 'UInt8Field',
    'Int16Field', 'UInt16Field',
    'Int32Field', 'UInt32Field',
    'Int64Field', 'UInt64Field',
    'Float32Field', 'Float64Field',
    'store_numbers_up_to',
]


class BasicBinaryField(core.BinaryField):

    initial_validators = []

    def __init__(self, label='', validators=None, order=None, **kwargs):
        core.BinaryItem.__init__(self)
        self.byte_width = struct.calcsize(self.pack_string)
        self.order = order
        all_validators = list(self.initial_validators)
        if validators is not None:
            all_validators.extend(validators)
        self.form_field = self.form_field_class(label,
                                                all_validators,
                                                **kwargs)

    def pack(self, data, order=None):
        order = self.order or order or ''
        return self.pack_data(data, order)

    def pack_data(self, data, order):
        return struct.pack(order + self.pack_string, data)

    def unpack(self, buf, order=None):
        order = self.order or order or ''
        return self.unpack_data(buf, order)

    def unpack_data(self, buf, order):
        return struct.unpack(order + self.pack_string, buf)[0]


class CharField(BasicBinaryField):

    form_field_class = wtforms.StringField
    initial_validators = [Length(min=1, max=1)]
    pack_string = 'c'


class BinaryBooleanField(BasicBinaryField):

    form_field_class = wtforms.BooleanField
    pack_string = '?'


class IntegerBinaryField(BasicBinaryField):

    form_field_class = wtforms.IntegerField

    @property
    def initial_validators(self):
        return [NumberRange(self.min, self.max)]


class Int8Field(IntegerBinaryField):

    pack_string = 'b'
    min = -128
    max = 127


class UInt8Field(IntegerBinaryField):

    pack_string = 'B'
    min = 0
    max = (2 ** 8) - 1


class Int16Field(IntegerBinaryField):

    pack_string = 'h'
    min = -(2 ** 15)
    max = (2 ** 15) - 1


class UInt16Field(IntegerBinaryField):

    pack_string = 'H'
    min = 0
    max = (2 ** 16) - 1


class Int32Field(IntegerBinaryField):

    pack_string = 'i'
    min = -(2 ** 31)
    max = (2 ** 31) - 1


class UInt32Field(IntegerBinaryField):

    pack_string = 'I'
    min = 0
    max = (2 ** 32) - 1


class Int64Field(IntegerBinaryField):

    pack_string = 'q'
    min = -(2 ** 63)
    max = (2 ** 63) - 1


class UInt64Field(IntegerBinaryField):

    pack_string = 'Q'
    min = 0
    max = (2 ** 64) - 1


class Float32Field(BasicBinaryField):

    form_field_class = wtforms.FloatField
    pack_string = 'f'


class Float64Field(BasicBinaryField):

    form_field_class = wtforms.FloatField
    pack_string = 'd'


class BytesField(BasicBinaryField):

    form_field_class = wtforms.StringField

    def __init__(self, label='', validators=None, max_length=None,
                 length=core.VARIABLE, order=None, **kwargs):

        if not isinstance(max_length, int) or max_length < 0:
            raise ValueError('BytesField must be created with a '
                             'positive max_length keyword argument.')

        self.order = order
        self.length = length

        self.max_length = max_length

        if self.length == core.FIXED:
            self.initial_validators = [Length(max=max_length, min=max_length)]
            self.pack_string = '{0}s'.format(max_length)

        elif self.length == core.VARIABLE:
            self.initial_validators = [Length(max=max_length)]
            self.pack_string = '{0}s'.format(max_length)

        elif self.length == core.EXPLICIT:
            self.initial_validators = [Length(max=max_length)]
            self.length_field = store_numbers_up_to(max_length, order=order)
            self.pack_string = '{0}{1}s'.format(self.length_field.pack_string,
                                                max_length)

        super(BytesField, self).__init__(label, validators, order, **kwargs)

    def pack_data(self, data, order):
        buf = bytearray(self.byte_width)
        length = len(data)
        if self.length == core.EXPLICIT:
            pack_length_string = order + self.length_field.pack_string
            struct.pack_into(pack_length_string, buf, 0, length)
            start = self.length_field.byte_width
        else:
            start = 0
        buf[start:start+length] = data
        return buf

    def unpack_data(self, buf, order):
        if self.length == core.EXPLICIT:
            unpack_length_string = order + self.length_field.pack_string
            length = struct.unpack_from(unpack_length_string, buf)[0]
            if length > self.max_length:
                message = "Buffer cannot contain {0} bytes.".format(length)
                raise ValueError(message)
            data_buf = buf[self.length_field.byte_width:]
        else:
            length = self.max_length
            data_buf = buf
        data = data_buf[:length]

        if self.length == core.VARIABLE:
            data = data.rstrip(b'\x00')

        return data


def store_numbers_up_to(n, signed=False, order=None):
    """
    Return a BinaryField class that can store numbers up to a certain maximum.
    """

    if signed:
        if n <= Int8Field.max:
            return Int8Field(order=order)
        elif n <= Int16Field.max:
            return Int16Field(order=order)
        elif n <= Int32Field.max:
            return Int32Field(order=order)
        elif n <= Int64Field.max:
            return Int64Field(order=order)
        else:
            raise ValueError("Can't track numbers up to {0}".format(n))
    else:
        if n <= UInt8Field.max:
            return UInt8Field(order=order)
        elif n <= UInt16Field.max:
            return UInt16Field(order=order)
        elif n <= UInt32Field.max:
            return UInt32Field(order=order)
        elif n <= UInt64Field.max:
            return UInt64Field(order=order)
        else:
            raise ValueError("Can't track numbers up to {0}".format(n))
