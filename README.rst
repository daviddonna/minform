Minform
=======

.. image:: https://img.shields.io/travis/daviddonna/minform.svg
   :target: https://travis-ci.org/daviddonna/minform
.. image:: http://img.shields.io/pypi/v/minform.svg
   :target: https://pypi.python.org/pypi/minform

The declarative ease of
`WTForms <https://github.com/wtforms/wtforms>`_, the small data
footprint of
`struct <https://docs.python.org/3/library/struct.html>`_.

For more detailed examples, read the full docs at
https://minform.readthedocs.org.

Why does Minform exist?
-----------------------

Let's talk about data size.

Say you have a fleet of devices with cell modems that report to a web server.
Here's an example of a data packet you might :

.. code-block:: c

    struct sensor_data {
        char version[8];
        char serial[12];
        int32_t latitude;    // fixed-point * 100000
        int32_t longitude;   // fixed-point * 100000
        int16_t temperature; // fixed-point * 100
        uint16_t pings;
        uint8_t battery_pct;
    };

Let's say they're reporting their data in JSON format, because that's lighter
than XML but still coherent to most server frameworks. Here's a data packet:

.. code-block:: javascript

    {
        "version": "1.0",
        "serial": "DEADBEEF",
        "latitude": 4071270,
        "longitude": -7400590,
        "temperature": 3200,
        "pings": 123,
        "battery_pct": 62
    }

If you take out all the whitespace, that's **144 bytes**. (ASCII encoding).
Maybe that's all you need, but maybe you need to store billions or trillions
of these little guys. Worse, maybe you need to pay through the tear ducts for
cellular data. It would be nice for that data to be smaller, and to be
predictably sized.

Besides, let's face it: serializing to JSON from C is a pain in the patoot.
Depending on the library, you could be looking at ten or twenty lines of code
(or a truly epic ``sprintf``), just to serialize a record.

On the Python side, we can probably just use a form library like WTForms to
validate incoming data, but we've already paid a price to make that data
server-friendly.

What can Minform do for me?
---------------------------

Let's build a Minform form to handle incoming sensor data.

.. code-block:: python

    from minform import *

    class SensorData(BinaryForm):

        order = LITTLE_ENDIAN  # let's say our devices are little-endian
        version = BytesField(max_length=8, length=AUTOMATIC)
        serial = BytesField(max_length=12, length=AUTOMATIC)
        latitude = Int32Field()
        longitude = Int32Field()
        temperature = Int16Field()
        pings = UInt16Field()
        battery_pct = UInt8Field()
        maintainer = BytesField(max_length=3, length=FIXED)
        padding = BlankBytes(3)

Here's the C code that will serialize your structure:

.. code-block:: c

    #include <string.h>

    void serialize(char *send_buffer, struct sensor_data data) {
        memcpy(send_buffer, &data, sizeof(struct sensor_data));
    }

And here's the Python that will receive it:

.. code-block:: python

    form = SensorData.unpack(serialized_data)

That serialized record is **36 bytes**. 36 on the wire, 36 in a file. You may
need to tweak the form definition, depending on your C compiler and the target
architecture, but Minforms gives you the tools to cope with padding bytes, and
even mixed byte ordering.

Let's fill in some gaps
-----------------------

Minforms are an awful lot like WTForms: you subclass ``minform.BinaryForm``,
and add ``BinaryField``\ s as class properties. Here's another quick example:

.. code:: python

    import minform

    class MyForm(minform.BinaryForm):
        '''
        This is a subclass of wtforms.Form: you can validate data with it,
        construct it from an HTML form, extract the data as a Python dict, etc.
        '''
        first_name = minform.BytesField('First Name', max_length=10)
        last_name = minform.BytesField('Last Name', max_length=10)
        age = minform.UInt8Field('Age')

    #               first_name (10)          last_name (10)           age (1)
    packed_data = b'David\x00\x00\x00\x00\x00Donna\x00\x00\x00\x00\x00\x18'
    form = MyForm.unpack(packed_data)
    assert form.data == {
        'first_name': b'David',
        'last_name': b'Donna',
        'age': 24,
    }

    next_form = MyForm(first_name=b'Foo', last_name=b'Barsson', age=100)
    packed = next_form.pack()
    assert packed == b'Foo\x00\x00\x00\x00\x00\x00\x00Barsson\x00\x00\x00\x64'

Because the library is built on ``struct``, binary serializations of a form's
data are in fixed-length buffers. This makes them easier to store, and easy to
map onto relatively naive serializations of C structs. It also allows for
clear documentation of the binary format, because the data maps predictably
onto different positions in a packed buffer.

Compound BinaryFields allow you to create nested structures that still
serialize into flat buffers.

.. code:: python

    class MyBigBadForm(minform.BinaryForm):
        """
        This is taking a turn for campy criminality.
        """
        riches = minform.Int16Field()
        goons = minform.BinaryFieldList(Person, max_entries=4, length=minform.EXPLICIT)

    squad = MyBigBadForm(riches=55223, goons=[
        {'first_name': 'Joey', 'last_name': 'Schmoey', 'age': 32},
        {'first_name': 'Manny', 'last_name': 'The Man', 'age': 40},
        {'first_name': 'Gerta', 'last_name': 'Goethe', 'age': 52},
    ])
    assert squad.pack() == (b'\xd7\xb7' +                                  # riches
                            b'\x03' +                                      # goons prefix
                            b'Joey\0\0\0\0\0\0Schmoey\0\0\0\x32' +         # goons[0]
                            b'Manny\0\0\0\0\0The Man\0\0\0\x40' +          # goons[1]
                            b'Gerta\0\0\0\0\0Goethe\0\0\0\0\x52' +         # goons[2]
                            b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0') # goons[3]

Even with an entire set of blank bytes for ``goons[3]``, that's 87 bytes, vs
185 for the JSON representation.
