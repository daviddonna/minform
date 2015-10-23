import pytest
import unittest
import wtforms
import minform


class TestBinaryItem(unittest.TestCase):

    class MyItem(minform.BinaryItem):

        size = 4

        def pack(self, data, order=None):
            return b'\x01\x02\x03\x04'

        def unpack(self, buf, order=None):
            return 0x01020304

    def test_binary_item_cannot_be_subclassed_without_pack(self):

        class MyItem(minform.BinaryItem):
            def unpack(self, buf, order=None):
                pass

        with pytest.raises(TypeError):
            MyItem()

    def test_binary_item_cannot_be_subclassed_without_unpack(self):

        class MyItem(minform.BinaryItem):
            def pack(self, data, order=None):
                pass

        with pytest.raises(TypeError):
            MyItem()

    def test_pack_into_works_for_same_size_buffer(self):
        m = self.MyItem()
        buf = bytearray(4)
        m.pack_into(buf, 0, None)
        assert buf == b'\x01\x02\x03\x04'

    def test_pack_into_fails_for_small_buffer(self):
        m = self.MyItem()
        buf = bytearray(3)
        with pytest.raises(ValueError):
            m.pack_into(buf, 0, None)

    def test_pack_into_fails_for_small_remaining_buffer(self):
        m = self.MyItem()
        buf = bytearray(5)
        with pytest.raises(ValueError):
            m.pack_into(buf, 2, None)

    def test_pack_into_fails_with_small_buffer_from_end(self):
        m = self.MyItem()
        buf = bytearray(5)
        with pytest.raises(ValueError):
            m.pack_into(buf, -3, None)

    def test_pack_into_succeeds_with_sufficient_buffer_from_end(self):
        m = self.MyItem()
        buf = bytearray(5)
        with pytest.raises(ValueError):
            m.pack_into(buf, -4, None)

    def test_unpack_from_works_for_same_size_buffer(self):
        m = self.MyItem()
        buf = b'\x01\x02\x03\x04'
        data = m.unpack_from(buf, 0, None)
        assert data == 0x01020304

    def test_unpack_from_fails_for_small_buffer(self):
        m = self.MyItem()
        buf = bytearray(3)
        with pytest.raises(ValueError):
            m.unpack_from(buf, 0, None)

    def test_unpack_from_fails_for_small_remaining_buffer(self):
        m = self.MyItem()
        buf = bytearray(5)
        with pytest.raises(ValueError):
            m.unpack_from(buf, 2, None)

    def test_unpack_from_fails_with_small_buffer_from_end(self):
        m = self.MyItem()
        buf = bytearray(5)
        with pytest.raises(ValueError):
            m.unpack_from(buf, -3, None)

    def test_unpack_from_succeeds_with_sufficient_buffer_from_end(self):
        m = self.MyItem()
        buf = bytearray(5)
        data = m.unpack_from(buf, -4, None)
        assert data == 0x01020304


class TestBinaryForm(unittest.TestCase):

    class Form(minform.BinaryForm):

        order = minform.BIG_ENDIAN

        char = minform.CharField()
        int32 = minform.Int32Field()
        bytes = minform.BytesField(max_length=6, length=minform.EXPLICIT)
        _ = minform.BlankBytes(3)
        lst = minform.BinaryFieldList(minform.UInt8Field(), max_entries=3,
                                      length=minform.FIXED)
        end = minform.BytesField(max_length=2, length=minform.AUTOMATIC)
        lst2 = minform.BinaryFieldList(minform.UInt16Field(), max_entries=1,
                                       length=minform.EXPLICIT)

    data = {
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

    buf = (b'\x10\x12\x34\x56\x78' +
           b'\x03foo\0\0\0' +
           b'\0\0\0\x01\x02\x03' +
           b'ab\x01\x12\x34')

    size = len(buf)

    def test_non_field_binary_items_are_removed_from_namespace(self):
        assert not hasattr(self.Form, '_')

    def test_binary_items_are_replace_with_fields(self):
        for name in 'char int32 bytes lst end lst2'.split():
            assert isinstance(getattr(self.Form, name),
                              wtforms.core.UnboundField)

    def test_binary_items_are_cached_in_list(self):
        assert len(self.Form._binary_items) == 7
        assert all(isinstance(f, minform.BinaryItem)
                   for f in self.Form._binary_items)

    def test_pack_into_works_for_same_size_buffer(self):
        form = self.Form(data=self.data)
        buf = bytearray(self.size)
        form.pack_into(buf, 0)
        assert buf == self.buf

    def test_pack_into_fails_for_small_buffer(self):
        m = self.Form(data=self.data)
        buf = bytearray(self.size - 1)
        with pytest.raises(ValueError):
            m.pack_into(buf, 0)

    def test_pack_into_fails_for_small_remaining_buffer(self):
        m = self.Form(data=self.data)
        buf = bytearray(self.size + 1)
        with pytest.raises(ValueError):
            m.pack_into(buf, 2)

    def test_pack_into_fails_with_small_buffer_from_end(self):
        m = self.Form(data=self.data)
        buf = bytearray(self.size + 1)
        with pytest.raises(ValueError):
            m.pack_into(buf, -(self.size - 1))

    def test_pack_into_succeeds_with_sufficient_buffer_from_end(self):
        m = self.Form(data=self.data)
        buf = bytearray(self.size + 1)
        with pytest.raises(ValueError):
            m.pack_into(buf, -self.size)

    def test_unpack_from_succeeds_for_same_size_buffer(self):
        form = self.Form.unpack_from(self.buf, 0)
        assert form.data == self.data

    def test_unpack_from_fails_for_small_buffer(self):
        with pytest.raises(ValueError):
            self.Form.unpack_from(self.buf[:-1], 0)

    def test_unpack_from_fails_for_small_remaining_buffer(self):
        buf = bytearray(self.size + 1)
        with pytest.raises(ValueError):
            self.Form.unpack_from(buf, 2)

    def test_unpack_from_fails_with_small_buffer_from_end(self):
        buf = bytearray(self.size + 1)
        with pytest.raises(ValueError):
            self.Form.unpack_from(buf, -(self.size - 1))

    def test_unpack_from_succeeds_with_sufficient_buffer_from_end(self):
        buf = b'\x00\x00' + self.buf
        form = self.Form.unpack_from(buf, -self.size)
        assert form.data == self.data
