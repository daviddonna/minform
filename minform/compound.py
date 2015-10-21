import wtforms

from . import core
from . import basic


class BinaryFieldList(core.BinaryField):

    def __init__(self, inner_field, label='', validators=None,
                 min_entries=0, max_entries=None,
                 length=core.VARIABLE, order=None,
                 **kwargs):
        core.BinaryField.__init__(self)
        if max_entries is None:
            raise ValueError("BinaryFieldList must have a max_entries "
                             "keyword argument.")
        if not isinstance(inner_field, core.BinaryField):
            raise ValueError("BinaryFieldList must contain a BinaryField.")

        self.max_entries = max_entries
        self.length = length
        self.order = order

        data_size = inner_field.size * max_entries
        if length == core.FIXED:
            self.size = data_size
        else:
            self.count_field = basic.store_numbers_up_to(max_entries,
                                                         order=order)
            self.size = self.count_field.size + data_size
            kwargs['default'] = []

        self.inner_field = inner_field
        unbound_field = self.inner_field.form_field
        self.form_field = wtforms.FieldList(unbound_field, label, validators,
                                            min_entries=min_entries,
                                            max_entries=max_entries,
                                            **kwargs)

    def pack(self, data, order=None):
        order = order or self.order
        buf = bytearray(self.size)

        if self.length == core.VARIABLE:
            packed_count = self.count_field.pack(len(data))
            buf[0:self.count_field.size] = packed_count
            start = self.count_field.size
        else:
            start = 0

        for item in data:
            stop = start + self.inner_field.size
            buf[start:stop] = self.inner_field.pack(item, order)
            start = stop

        return buf

    def unpack(self, buf, order=None):
        order = order or self.order
        data = []

        if self.length == core.VARIABLE:
            count_chunk = buf[0:self.count_field.size]
            data_length = self.count_field.unpack(count_chunk)
            if data_length > self.max_entries:
                raise ValueError("Unreasonable count of {0} for {1}".format(
                    data_length, self.name))
            start = self.count_field.size
        else:
            data_length = self.max_entries
            start = 0

        for i in range(data_length):
            stop = start + self.inner_field.size
            chunk = buf[start:stop]
            data.append(self.inner_field.unpack(chunk, order))
            start = stop

        return data


class BinaryFormField(core.BinaryField):

    def __init__(self, form_class, label='', validators=None, order=None,
                 **kwargs):
        core.BinaryField.__init__(self)

        self.order = order
        if not issubclass(form_class, core.BinaryForm):
            raise ValueError("BinaryFormField must wrap a BinaryForm.")

        self.form_class = form_class
        self.form_field = wtforms.FormField(form_class, label, validators,
                                            **kwargs)
        self.size = form_class.size

    def pack(self, data, order=None):
        order = order or self.order
        return self.form_class(data=data).pack(order)

    def unpack(self, buf, order=None):
        order = order or self.order
        return self.form_class.unpack(buf, order=order).data
