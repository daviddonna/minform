import pytest
import wtforms
import minform

from . import util


class TestBlankField(util.FormTest):

    class Form(minform.BinaryForm):
        a = minform.BlankBytes(4)

    def test_blank_bytes_are_not_a_field(self):
        assert self.Form._unbound_fields is None

    def test_blank_bytes_count_toward_size(self):
        assert self.Form.size == 4

    def test_unpack_blank_bytes(self):
        self.Form.unpack(b'\x00\x00\x00\x00')

    def test_pack_blank_bytes(self):
        form = self.Form()
        assert form.pack() == b'\x00\x00\x00\x00'


class TestExplicitFieldList(util.FormTest):

    class Form(minform.BinaryForm):

        stuff = minform.BinaryFieldList(minform.UInt16Field(),
                                        max_entries=4,
                                        length=minform.EXPLICIT)

    def test_size_includes_count_and_data(self):
        assert self.Form.size == 1 + 4 * 2

    def test_binary_field_list_requires_max_entries(self):
        with pytest.raises(ValueError):
            class Form(minform.BinaryForm):
                l = minform.BinaryFieldList(minform.CharField())

    def test_binary_field_list_requires_binary_field(self):
        with pytest.raises(ValueError):
            class Form(minform.BinaryForm):
                l = minform.BinaryFieldList(wtforms.StringField,
                                            max_entries=3)

    def test_valid_data_is_valid(self):
        data_sets = [
            [],
            [0xA001],
            [0x0001, 0x0002],
            [0x0001, 0x0002, 0x00A1],
            [0x0001, 0x0002, 0xFFA1, 0x00FF],
        ]
        for data in data_sets:
            form = self.Form(stuff=data)
            assert form.validate()

    def test_invalid_data_is_valid(self):
        data_sets = [
            0x0011,
            [0x0001, 0x0002, 0xFFA1, 0x00FF, 0x1111],
        ]
        for data in data_sets:
            with pytest.raises(Exception):
                form = self.Form(stuff=data)
                assert not form.validate()

    def test_valid_data_packs(self):
        pairs = [
            (
                [],
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            ),
            (
                [0xA001],
                b'\x01\xA0\x01\x00\x00\x00\x00\x00\x00'
            ),
            (
                [0x0001, 0x0002],
                b'\x02\x00\x01\x00\x02\x00\x00\x00\x00'
            ),
            (
                [0x0001, 0x0002, 0x00A1],
                b'\x03\x00\x01\x00\x02\x00\xA1\x00\x00'
            ),
            (
                [0x0001, 0x0002, 0xFFA1, 0x00FF],
                b'\x04\x00\x01\x00\x02\xFF\xA1\x00\xFF'
            ),
        ]
        for data, buf in pairs:
            form = self.Form(stuff=data)
            assert form.pack(order=minform.BIG_ENDIAN) == buf

    def test_valid_data_unpacks(self):
        pairs = [
            (
                [],
                b'\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            ),
            (
                [0xA001],
                b'\x01\xA0\x01\x00\x00\x00\x00\x00\x00'
            ),
            (
                [0x0001, 0x0002],
                b'\x02\x00\x01\x00\x02\x00\x00\x00\x00'
            ),
            (
                [0x0001, 0x0002, 0x00A1],
                b'\x03\x00\x01\x00\x02\x00\xA1\x00\x00'
            ),
            (
                [0x0001, 0x0002, 0xFFA1, 0x00FF],
                b'\x04\x00\x01\x00\x02\xFF\xA1\x00\xFF'
            ),
        ]
        for data, buf in pairs:
            form = self.Form.unpack(buf, order=minform.BIG_ENDIAN)
            assert form.data == dict(stuff=data)

    def test_unreasonable_data_count_is_flagged(self):
        with pytest.raises(ValueError):
            self.Form.unpack(b'\x05\x00\x00\x00\x00\x00\x00\x00\x00')


class TestFixedFieldList(util.FormTest):

    class Form(minform.BinaryForm):
        stuff = minform.BinaryFieldList(minform.UInt16Field(),
                                        max_entries=3,
                                        length=minform.FIXED,
                                        order=minform.BIG_ENDIAN)

    def test_size_is_data_size(self):
        assert self.Form.size == 3 * 2

    def test_valid_data_unpacks(self):
        buf = b'\x11\x22\x33\x44\x55\x66'
        form = self.Form.unpack(buf)
        assert form.data == dict(stuff=[0x1122, 0x3344, 0x5566])

    def test_valid_data_packs(self):
        form = self.Form(stuff=[0x1122, 0x3344, 0x5566])
        buf = b'\x11\x22\x33\x44\x55\x66'
        assert form.pack() == buf


class F2(minform.BinaryForm):
    char = minform.CharField()
    int32 = minform.Int32Field()
    bytes = minform.BytesField(max_length=6, length=minform.EXPLICIT)
    _ = minform.BlankBytes(3)
    lst = minform.BinaryFieldList(minform.UInt8Field(), max_entries=3,
                                  length=minform.FIXED)
    end = minform.BytesField(max_length=2, length=minform.AUTOMATIC)
    lst2 = minform.BinaryFieldList(minform.UInt16Field(), max_entries=1,
                                   length=minform.EXPLICIT)


class TestBinaryFormField(util.FormTest):

    data = {
        'f': {
            'char': b'\x10',
            'int32': 0x12345678,
            'bytes': b'foo',
            'lst': [
                0x01,
                0x02,
                0x03,
            ],
            'end': b'ab',
            'lst2': [0x1234]
        }
    }

    buf = (b'\x10\x12\x34\x56\x78' +
           b'\x03foo\0\0\0' +
           b'\0\0\0\x01\x02\x03' +
           b'ab\x01\x12\x34')

    size = len(buf)

    class Form(minform.BinaryForm):
        f = minform.BinaryFormField(F2, order=minform.BIG_ENDIAN)

    def test_form_has_proper_size(self):
        assert self.Form.size == self.size

    def test_form_can_be_constructed(self):
        form = self.Form(data=self.data)
        assert form.validate()

    def test_form_can_be_packed(self):
        form = self.Form(data=self.data)
        buf = form.pack()
        assert buf == self.buf

    def test_form_can_be_unpacked(self):
        form = self.Form.unpack(self.buf)
        assert form.data == self.data

    def test_binary_form_field_requires_binary_form(self):
        class F1(wtforms.Form):
            pass

        with pytest.raises(ValueError):
            class F2(minform.BinaryForm):
                f = minform.BinaryFormField(F1)
