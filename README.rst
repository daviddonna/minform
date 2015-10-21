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
`protocol buffers <https://developers.google.com/protocol-buffers/>`__,
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
    unpacked_form = MyForm.unpack()
    assert form.data == {'first_name': 'David', 'last_name': 'Donna', 'age': 24}

    next_form = MyForm(first_name='Foo', last_name='Barsson', age='100')
    packed = next_form.pack()
    assert packed == b'Foo\x00\x00\x00\x00\x00\x00\x00Barsson\x00\x00\x00\x64'

For more detailed examples, read the full docs at
https://minform.readthedocs.org. (Coming soon!)
