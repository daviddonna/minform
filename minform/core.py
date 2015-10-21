import abc
import six
import wtforms

__all__ = [
    'FIXED', 'VARIABLE', 'EXPLICIT',
    'NATIVE', 'LITTLE_ENDIAN', 'BIG_ENDIAN', 'NETWORK',
    'BinaryItem', 'BlankBytes', 'BinaryField', 'BinaryForm',
]

FIXED = 'fixed'
VARIABLE = 'variable'
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

    order = None
    form_field = None

    def __init__(self):
        self._creation_id = _new_creation_id()

    @abc.abstractmethod
    def pack(self, data, order=None):
        pass  # pragma: no cover

    @abc.abstractmethod
    def unpack(self, buf, order=None):
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

    name = None

    def __init__(self, size):
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

    order = None

    @classmethod
    def unpack(cls, buf, order=None):
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
