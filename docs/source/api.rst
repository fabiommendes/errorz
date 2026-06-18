API Reference
=============

.. warning:: 

   Sphinx autodoc is used to generate this documentation. It does not do a 
   particularly good job at rendering type annotations, so trust your API 
   or the code itself over the documentation shown here.

   All functions are fully typed and the type annotations are mostly correct.

Error class
-----------

.. autoclass:: errorz.Err
   :members:


Creating and testing results
----------------------------

.. autofunction:: errorz.ok
.. autofunction:: errorz.err
.. autofunction:: errorz.is_err


Unwrapping
----------

.. autofunction:: errorz.unwrap
.. autofunction:: errorz.expect
.. autofunction:: errorz.check
.. autofunction:: errorz.unwrap_lazy


Function calls
--------------

.. autofunction:: errorz.call
.. autofunction:: errorz.call_checked
.. autofunction:: errorz.catch


Mapping, zipping and combining
------------------------------

.. autofunction:: errorz.map
.. autofunction:: errorz.zip
.. autofunction:: errorz.coalesce
.. autofunction:: errorz.separate


Iterators, sequences, and other collections
-------------------------------------------

.. autofunction:: errorz.iter
.. autofunction:: errorz.some
.. autofunction:: errorz.filter
.. autofunction:: errorz.filter_values
.. autofunction:: errorz.non_empty
.. autofunction:: errorz.single


Testing with Hypothesis
-----------------------

.. autofunction:: errorz.hypothesis.result
.. autofunction:: errorz.hypothesis.exceptions
.. autofunction:: errorz.hypothesis.errors
.. autofunction:: errorz.hypothesis.error_messages

