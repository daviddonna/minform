import pytest
import struct
import unittest
from wtforms.validators import NumberRange
import minform

from . import util

up_to_ten = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'


class TestCharField(util.FormTest):

    class Form(minform.BinaryForm):
        char = minform.CharField()

    def test_form_has_field(self):
        assert len(self.Form._binary_items) == 1

    def test_char_field_can_be_loaded(self):
        form = self.Form(char='x')
        assert form.validate()
        assert form.data == {'char': 'x'}

    def test_char_field_refuses_empty_string(self):
        form = self.Form(char='')
        assert not form.validate()

    def test_char_field_refuses_long_string(self):
        form = self.Form(char='ab')
        assert not form.validate()

    def test_char_field_can_pack(self):
        form = self.Form(char=b'\x02')
        assert form.validate()
        b = form.pack()
        assert b == b'\x02'

    def test_char_field_can_unpack(self):
        form = self.Form.unpack(b'\x33')
        assert form.data == dict(char=b'\x33')


class IntField(object):

    def setUp(self):
        class Form(minform.BinaryForm):
            n = self.integer_field('n')
        self.Form = Form

    def test_too_small_number_is_rejected(self):
        n = self.integer_field.min - 1
        form = self.Form(n=n)
        assert not form.validate()

    def test_too_large_number_is_rejected(self):
        n = self.integer_field.max + 1
        form = self.Form(n=n)
        assert not form.validate()

    def test_min_number_is_accepted(self):
        n = self.integer_field.min
        form = self.Form(n=n)
        assert form.validate()

    def test_max_number_is_accepted(self):
        n = self.integer_field.max
        form = self.Form(n=n)
        assert form.validate()

    def test_zero_is_accepted(self):
        if 0 >= self.integer_field.min and 0 <= self.integer_field.max:
            form = self.Form(n=0)
            assert form.validate()

    def test_min_number_can_pack(self):
        n = self.integer_field.min
        form = self.Form(n=n)
        buf = form.pack()
        assert len(buf) == self.integer_field().size

    def test_max_number_can_pack(self):
        n = self.integer_field.max
        form = self.Form(n=n)
        buf = form.pack()
        assert len(buf) == self.integer_field().size

    def test_explicit_little_endian_deserialization(self):
        temp = self.integer_field()
        big_buf = b'\x00\x01\x02\x03\x04\x05\x06\x07'[:temp.size]
        little_value = struct.unpack('<' + temp.pack_string, big_buf)[0]
        form = self.Form.unpack(big_buf, order=minform.LITTLE_ENDIAN)
        assert form.data == dict(n=little_value)

    def test_implicit_little_endian_deserialization(self):
        temp = self.integer_field(order=minform.LITTLE_ENDIAN)

        class Form(minform.BinaryForm):
            n = self.integer_field(order=minform.LITTLE_ENDIAN)

        buf = b'\x00\x01\x02\x03\x04\x05\x06\x07'[:temp.size]
        little_value = struct.unpack('<' + temp.pack_string, buf)[0]
        form = Form.unpack(buf)
        assert form.data == dict(n=little_value)


class TestInt8Field(IntField, util.FormTest):
    integer_field = minform.Int8Field

    def test_extra_validators_are_passed_in(self):

        class Form(minform.BinaryForm):
            n = minform.UInt8Field(validators=[NumberRange(max=10)])

        form = Form(n=-1)
        assert not form.validate()

        form2 = Form(n=11)
        assert not form2.validate()


class TestUInt8Field(IntField, util.FormTest):
    integer_field = minform.UInt8Field


class TestInt16Field(IntField, util.FormTest):
    integer_field = minform.Int16Field


class TestUInt16Field(IntField, util.FormTest):
    integer_field = minform.UInt16Field


class TestInt32Field(IntField, util.FormTest):
    integer_field = minform.Int32Field


class TestUInt32Field(IntField, util.FormTest):
    integer_field = minform.UInt32Field


class TestInt64Field(IntField, util.FormTest):
    integer_field = minform.Int64Field


class TestUInt64Field(IntField, util.FormTest):
    integer_field = minform.UInt64Field


class TestFloat32Field(util.FormTest):

    class Form(minform.BinaryForm):
        f = minform.Float32Field()


class TestFloat64Field(util.FormTest):

    class Form(minform.BinaryForm):
        f = minform.Float64Field()


class TestBinaryBooleanField(util.FormTest):

    class Form(minform.BinaryForm):
        b = minform.BinaryBooleanField()

    def test_can_load_with_true(self):
        form = self.Form(b=True)
        assert form.validate()

    def test_can_load_with_false(self):
        form = self.Form(b=False)
        assert form.validate()

    def test_can_unpack_true(self):
        form = self.Form.unpack(b'\x01')
        assert form.data == dict(b=True)

    def test_can_unpack_false(self):
        form = self.Form.unpack(b'\x00')
        assert form.data == dict(b=False)

    def test_can_pack_true(self):
        form = self.Form(b=True)
        assert form.pack() == b'\x01'

    def test_can_pack_false(self):
        form = self.Form(b=False)
        assert form.pack() == b'\x00'


class TestFixedBytesField(unittest.TestCase):

    class Form(minform.BinaryForm):
        ten = minform.BytesField(max_length=10, length=minform.FIXED)
        empty = minform.BytesField(max_length=0)

    def check(self, buf):
        form = self.Form.unpack(buf)
        assert form.data == dict(ten=buf, empty=b'')
        assert form.pack() == buf

    def test_bytes_field_needs_max_length(self):
        with pytest.raises(ValueError):

            class Form(minform.BinaryForm):
                s = minform.BytesField(label='foo')

    def test_empty_field_has_width_0(self):
        assert self.Form.size == 10

    def test_fields_load_together(self):
        buf = up_to_ten
        form = self.Form.unpack(buf)
        assert form.data == dict(ten=buf, empty=b'')

    def test_terminal_null_byte(self):
        self.check(b'123456789\x00')

    def test_null_string(self):
        self.check(b'\x00' * 10)


class TestExplicitBytesField(unittest.TestCase):

    class ShortForm(minform.BinaryForm):
        s = minform.BytesField(max_length=10, length=minform.EXPLICIT)

    class LongForm(minform.BinaryForm):
        s = minform.BytesField(max_length=256, length=minform.EXPLICIT)

    def test_empty_field_has_width_zero(self):
        assert self.ShortForm.size == 11

    def test_fields_load_together(self):
        buf = b'\x0A' + up_to_ten
        form = self.ShortForm.unpack(buf)
        assert form.data == dict(s=up_to_ten)

    def test_read_stops_at_limit(self):
        buf = b'\x05' + up_to_ten
        form = self.ShortForm.unpack(buf)
        assert form.data == dict(s=b'\x00\x01\x02\x03\x04')

    def test_read_can_be_zero(self):
        buf = b'\x00' + up_to_ten
        form = self.ShortForm.unpack(buf)
        assert form.data == dict(s=b'')

    def test_larger_buffer_has_larger_count(self):
        assert self.LongForm.size == 258

    def test_invalid_count_is_flagged(self):
        with pytest.raises(ValueError):
            buf = b'\x0B' + up_to_ten
            self.ShortForm.unpack(buf)

    def test_bytes_field_packs_correctly(self):
        f = self.ShortForm(s=b'foo')
        buf = f.pack()
        assert buf == b'\x03foo\x00\x00\x00\x00\x00\x00\x00'


class TestVariableBytesField(util.FormTest):

    class Form(minform.BinaryForm):
        s = minform.BytesField(max_length=10, length=minform.AUTOMATIC)

    def test_full_bufer_stops_naturally(self):
        buf = up_to_ten
        form = self.Form.unpack(buf)
        assert form.data == dict(s=buf)

    def test_stops_before_trailing_null_bytes(self):
        bufs = [
            b'\x11\x22\x33\x44\x55\x66\x77\x88\x99\x00',
            b'\x11\x22\x33\x44\x55\x66\x77\x88\x00\x00',
            b'\x11\x22\x33\x44\x55\x66\x77\x00\x00\x00',
            b'\x11\x22\x33\x44\x55\x66\x00\x00\x00\x00',
            b'\x11\x22\x33\x44\x55\x00\x00\x00\x00\x00',
            b'\x11\x22\x33\x44\x00\x00\x00\x00\x00\x00',
            b'\x11\x22\x33\x00\x00\x00\x00\x00\x00\x00',
            b'\x11\x22\x00\x00\x00\x00\x00\x00\x00\x00',
            b'\x11\x00\x00\x00\x00\x00\x00\x00\x00\x00',
            b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        ]

        for buf in bufs:
            form = self.Form.unpack(buf)
            assert form.data == dict(s=buf.rstrip(b'\x00'))


class TestStoreNumbersUpTo(unittest.TestCase):

    def test_unsigned_fields_correspond_to_numbers(self):
        mapping = [
            (0, minform.UInt8Field),
            (100, minform.UInt8Field),
            (255, minform.UInt8Field),
            (256, minform.UInt16Field),
            (500, minform.UInt16Field),
            (2**16 - 1, minform.UInt16Field),
            (2**16, minform.UInt32Field),
            (2**20, minform.UInt32Field),
            (2**32 - 1, minform.UInt32Field),
            (2**32, minform.UInt64Field),
            (2**40, minform.UInt64Field),
            (2**64 - 1, minform.UInt64Field),
        ]
        for n, typ in mapping:
            assert isinstance(minform.basic.store_numbers_up_to(n), typ)

    def test_signed_fields_correspond_to_numbers(self):
        mapping = [
            (0, minform.Int8Field),
            (100, minform.Int8Field),
            (127, minform.Int8Field),
            (128, minform.Int16Field),
            (500, minform.Int16Field),
            (2**15 - 1, minform.Int16Field),
            (2**15, minform.Int32Field),
            (2**20, minform.Int32Field),
            (2**31 - 1, minform.Int32Field),
            (2**31, minform.Int64Field),
            (2**40, minform.Int64Field),
            (2**63 - 1, minform.Int64Field),
        ]
        for n, typ in mapping:
            assert isinstance(minform.basic.store_numbers_up_to(n, True), typ)

    def test_unsigned_field_max(self):
        with pytest.raises(ValueError):
            minform.basic.store_numbers_up_to(2 ** 64)

    def test_signed_field_max(self):
        with pytest.raises(ValueError):
            minform.basic.store_numbers_up_to(2 ** 63, True)
