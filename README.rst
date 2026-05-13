===================
Layered Config Tree
===================

----

**NOTE: This repository has been archived.**

Development has moved to the `vivarium-suite monorepo
<https://github.com/ihmeuw/vivarium-suite>`_, where this code now lives at
``libs/config-tree/``. The package has been renamed and is published as
``vivarium-config-tree`` on PyPI and imported as ``vivarium.config_tree``. The
primary class ``LayeredConfigTree`` has been renamed to ``ConfigTree``.

This repository's final release is v4.1.8: a shim that contains no code and only
declares ``vivarium-config-tree>=5.0.0`` as a dependency. No further releases will
be cut from this repository. File issues and PRs against ``vivarium-suite`` instead.

**Existing users do not need to change anything immediately.** ``pip install
layered_config_tree`` continues to work (the v4.1.8 shim transparently installs
``vivarium-config-tree``), and ``import layered_config_tree`` continues to work (temporarily)
via the ``vivarium-compat`` import shim (with a ``DeprecationWarning``). Update at
your own pace.

To migrate fully to the new package:

**Install:**

.. code-block:: bash

   pip install vivarium-config-tree   # was: pip install layered_config_tree

**Import:**

.. code-block:: python

   import vivarium.config_tree                       # was: import layered_config_tree
   from vivarium.config_tree import ConfigTree       # was: from layered_config_tree import LayeredConfigTree

The class rename is a *two-step* migration when consumed through the import shim:
``from layered_config_tree import LayeredConfigTree`` still works because
``LayeredConfigTree`` is kept as a deprecated alias on the new module. To clear the
deprecation warnings entirely, update both the import path and the class name to
their new forms above.

----

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
