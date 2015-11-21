import wtforms

from . import core
from . import basic


class BinaryFieldList(core.BinaryField):

    """
    Store a homogeneous list of information.

    .. attribute:: inner_field

        A :class:`~wtforms.BinaryField`

    .. attribute:: max_entries

        The maximum number of items that can be stored in the list.

    .. attribute:: length

        A :ref:`length` constant.

    .. attribute:: size

        If :attr:`length` is :data:`minform.FIXED`, *size* will be equal to
        ``max_size * inner_field.length``.

        If :attr:`length` is :data:`minform.EXPLICIT`, *size* will be
        ``prefix_length + (max_size * inner_field.length)``. The value of
        ``prefix_length`` follows the documentation for :ref:`length`.

    .. attribute:: form_field
        :annotation: : wtforms.FieldList
    """

    def __init__(self, inner_field, label='', validators=None,
                 max_entries=None, length=core.EXPLICIT, order=None,
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
                                            max_entries=max_entries, **kwargs)

    def pack(self, data, order=None):
        order = order or self.order
        buf = bytearray(self.size)

        if self.length == core.EXPLICIT:
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

        if self.length == core.EXPLICIT:
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

    """
    Nest one :class:`~minform.BinaryForm` inside another.

    .. attribute:: form_class

        The :class:`~minform.BinaryForm` that describes the contents of this
        field. A :class:`BinaryFormField` instance will have the same
        :attr:`~BinaryItem.size` as its :attr:`form_class`, and will pack and
        unpack data in the same ways.

    .. attribute:: form_field
        :annotation: : wtforms.FormField
    """

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
