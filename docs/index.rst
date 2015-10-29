.. minform documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=======
Minform
=======

.. toctree::
   :maxdepth: 1

   api
   minform
   contributing
   authors

This package is available on github, at https://github.com/daviddonna/minform.

Installation
============

At the command line::

    $ easy_install minform

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv minform
    $ pip install minform

Examples
========

A simple BinaryForm might look like this:

.. code:: python

    import minform

    class Person(minform.BinaryForm):
        '''
        This is a subclass of wtforms.Form: you can validate data with it,
        construct it from an HTML form, extract the data as a Python dict, etc.
        '''
        first_name = minform.BytesField('First Name', max_length=10)
        last_name = minform.BytesField('Last Name', max_length=10)
        age = minform.UInt8Field('Age')

    #               first_name (10)          last_name (10)           age (1)
    packed_data = b'David\x00\x00\x00\x00\x00Donna\x00\x00\x00\x00\x00\x18'
    form = Person.unpack(packed_data)
    assert form.data == {
        'first_name': b'David',
        'last_name': b'Donna',
        'age': 24,
    }

    next_form = Person(first_name=b'Foo', last_name=b'Barsson', age=100)
    packed = next_form.pack()
    assert packed == b'Foo\x00\x00\x00\x00\x00\x00\x00Barsson\x00\x00\x00\x64'

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

For more information, see the API doc.