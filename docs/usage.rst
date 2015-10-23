========
Usage
========

.. _WTForms: https://wtforms.readthedocs.org/
.. _wtforms.Form: https://wtforms.readthedocs.org/en/latest/forms.html
.. _wtforms.Field: https://wtforms.readthedocs.org/en/latest/fields.html
.. _BinaryForm: minform.html#minform.core.BinaryForm
.. _BinaryField: minform.html#minform.core.BinaryField

This documentation assumes that you're somewhat familiar with `WTForms`_,
since Minform is intentionally similar to (and substantively derived from)
that project.

Minform provides a `BinaryForm`_ class, which subclasses from `wtforms.Form`_.
Instead of subclassing ``wtforms.Form`` with `wtforms.Field`_ instances as
class variables, you need to subclass ``minform.BinaryForm``, and give it
`BinaryField`_ instances as class variables. The result will be a ``Form``
with additional `pack <minform.html#minform.core.BinaryForm.pack>` and `unpack
<minform.html#minform.core.BinaryForm.unpack>` methods.
