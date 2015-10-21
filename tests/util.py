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
