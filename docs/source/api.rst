API Reference
=============

.. warning:: 

   Sphinx autodoc is used to generate this documentation. It does not do a 
   particularly good job at rendering type annotations, so trust your API 
   or the code itself over the documentation shown here.

   All functions are fully typed and the type annotations are mostly correct.

Unwrapping options
------------------

.. autofunction:: opt.unwrap
.. autofunction:: opt.unwrap_or
.. autofunction:: opt.unwrap_or_else
.. autofunction:: opt.expect


Mapping over options
--------------------

.. autofunction:: opt.map
.. autofunction:: opt.call


Zipping and combining options
-----------------------------

.. autofunction:: opt.zip
.. autofunction:: opt.together


Iterating over options
----------------------

.. autofunction:: opt.iter
.. autofunction:: opt.elements
.. autofunction:: opt.values