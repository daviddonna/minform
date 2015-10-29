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

Why does Minform exist?
-----------------------

Because I wanted to write declarative data schemas, like Google's
`protocol buffers <https://developers.google.com/protocol-buffers/>`_,
but with a little more power on the Python end.

What can Minform do for me?
---------------------------

Minform can add a lightweight binary protocol to your WTForms forms, or
add validation and web form input to your binary protocols.

How does Minform work?
----------------------

An awful lot like WTForms: you subclass ``minform.BinaryForm``, and add
``BinaryField``\ s as class properties. Here's a quick example:

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
        riches = minforms.Int16Field()
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
                            b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0)  # goons[3]

For more detailed examples, read the full docs at
https://minform.readthedocs.org.
