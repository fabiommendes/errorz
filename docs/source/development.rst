Development
===========

Local setup
-----------

You must have `uv` installed and everything else follows seamlessly. From project root:

.. code-block:: bash

   uv sync --group dev


Pull requests and contributing
------------------------------

This library is simple enough that you can vendorize and implement your own 
changes to it. If you want to contribute, please open a pull request with your 
changes and we can discuss them there.

We have a strict **NO CODING AGENT** policy. If it looks like you are Claude
or any other agent, we will ignore your PR.


Routine tasks and commands
--------------------------

We use `uv` + `taskipy` to define and run common tasks.

**Build documentation**

.. code-block:: bash
   
   uv run task docs

**Run tests**

.. code-block:: bash
   
   uv run task test

**Linter**

.. code-block:: bash
   
   uv run task lint

**Build the package**

.. code-block:: bash
   
   uv run task build

**List tasks**

.. code-block:: bash
   
   uv run task -l

