===================
Layered Config Tree
===================

**NOTE: This repository is archived and will receive no further updates.**

The ``layered_config_tree`` package has been renamed and migrated into the
`vivarium-suite monorepo <https://github.com/ihmeuw/vivarium-suite>`_.

What changed
------------

- **PyPI distribution:** ``layered_config_tree`` -> ``vivarium-config-tree``
- **Import path:** ``layered_config_tree`` -> ``vivarium.config_tree``
- **Class rename:** ``LayeredConfigTree`` -> ``ConfigTree``
- **Source:** ``ihmeuw/layered_config_tree`` (archived) ->
  ``ihmeuw/vivarium-suite`` (under ``libs/config-tree/``)
- **Docs:** https://vivarium-config-tree.readthedocs.io/

The final release on PyPI (``v4.1.9``) ships the same code as ``v4.1.7`` (``v4.1.8``
is a yanked version that included now-abandoned backwards compatibility shims) with
this banner added. ``pip install layered_config_tree`` will keep resolving and
importing as it did in ``v4.1.7``, but the code is frozen and will not receive
updates.

To migrate fully to the new package
-----------------------------------

New development should install ``vivarium-config-tree`` and import from ``vivarium.config_tree``.

**Install:**

.. code-block:: bash

    pip install vivarium-config-tree  # was: pip install layered_config_tree

**Import:**

.. code-block:: python

    from vivarium.config_tree import ConfigTree  # was: from layered_config_tree import LayeredConfigTree

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
