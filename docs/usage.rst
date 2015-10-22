========
Usage
========

.. _WTForms: https://wtforms.readthedocs.org/
.. _wtforms.Form: https://wtforms.readthedocs.org/en/latest/forms.html
.. _wtforms.Field: https://wtforms.readthedocs.org/en/latest/fields.html

This documentation assumes that you're somewhat familiar with `WTForms`_,
since Minform is intentionally similar to (and substantively derived from)
that project.

Minform provides a :ref:`class BinaryForm` class, which subclasses from
`wtforms.Form`_. Instead of subclassing ``wtforms.Form`` with ``wtforms.Field``
instances as class variables, you need to subclass ``minform.BinaryForm``, and
give it ``wtforms.BinaryField`` instances as class variables. The result will
be a ``Form`` with additional ``pack`` and ``unpack`` methods.

.. automodule:: minform.basic
    .. autofunction:: minform.basic.store_numbers_up_to