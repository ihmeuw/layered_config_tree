===================
Layered Config Tree
===================

**NOTE: This repository has been archived.**

The ``layered_config_tree`` package has been renamed and migrated into the
`vivarium-suite monorepo <https://github.com/ihmeuw/vivarium-suite>`_.

What changed
------------

- **PyPI distribution:** ``layered_config_tree`` -> ``vivarium-config-tree``
- **Import path:** ``layered_config_tree`` -> ``vivarium.config_tree``
- **Source:** ``ihmeuw/layered_config_tree`` (archived) ->
  ``ihmeuw/vivarium-suite`` (under ``libs/config-tree/``)
- **Docs:** https://vivarium-config-tree.readthedocs.io/

What this last release (v4.2.0) is
----------------------------------

A backward-compatibility shim; installing it pulls in:

- ``vivarium-engine>=5.0.0`` - the real implementation under the new import path.
- ``vivarium-compat>=0.6.0`` - an import hook that lets ``import vivarium``
  continue to work, emitting a ``DeprecationWarning``. Update your imports before
  the hook is removed.

If you depend on a specific pre-rename version (e.g. ``vivarium==4.1.5``),
pin to that version - those earlier releases still ship the original module
and continue to install standalone.

To migrate fully to the new package
-----------------------------------

**Install:**

.. code-block:: bash

    pip install vivarium-engine  # was: pip install vivarium

**Import:**

.. code-block:: python

    import vivarium.engine  # was: import vivarium

.. note::
    
    The class rename is a *two-step* migration when consumed through the import shim:
    ``from layered_config_tree import LayeredConfigTree`` still works because
    ``LayeredConfigTree`` is kept as a deprecated alias on the new module. To clear the
    deprecation warnings entirely, update both the import path and the class name to
    their new forms above.

Original package overview
=========================

Layered Config Tree is a configuration structure that supports cascading layers.

**Supported Python versions: 3.10, 3.11, 3.12, 3.13**

You can install ``layered_config_tree`` from PyPI with pip:

  ``> pip install layered_config_tree``

or build it from from source:

  ``> git clone https://github.com/ihmeuw/layered_config_tree.git``

  ``> cd layered_config_tree``

  ``> conda create -n ENVIRONMENT_NAME python=3.13``

  ``> pip install .``

This will make the ``layered_config_tree`` library available to python.
