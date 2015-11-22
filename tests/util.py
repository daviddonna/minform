import unittest
import pytest


class FormTest(unittest.TestCase):

    valid_inputs = []
    invalid_inputs = []

    def test_form_cannot_unpack_too_little_data(self):
        size = self.Form.size
        if size > 0:
            with pytest.raises(ValueError):
                self.Form.unpack(b'\x00' * (size - 1))

    def test_form_cannot_unpack_too_much_data(self):
        size = self.Form.size
        with pytest.raises(ValueError):
            self.Form.unpack(b'\x00' * (size + 1))

    def test_valid_inputs_are_accepted(self):
        for valid_input in self.valid_inputs:
            self.Form.unpack(valid_input)

    def test_invalid_inputs_are_not_accepted(self):
        for invalid_input in self.invalid_inputs:
            with pytest.raises(ValueError):
                self.Form.unpack(invalid_input)

    def test_form_can_unpack_from_exactly_sized_buffer(self):
        buffer = b'\0' * self.Form.size
        self.Form.unpack_from(buffer, 0)

    def test_form_cannot_unpack_from_small_buffer(self):
        buffer = b'\0' * (self.Form.size - 1)
        with pytest.raises(ValueError):
            self.Form.unpack_from(buffer, 0)

    def test_form_can_unpack_from_partway_along_buffer(self):
        buffer = b'\0' * (self.Form.size + 3)
        self.Form.unpack_from(buffer, 2)

    def test_form_can_unpack_from_exact_negative_index(self):
        buffer = b'\0' * self.Form.size
        self.Form.unpack_from(buffer, -self.Form.size)
