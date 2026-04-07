.. _getting_started_tutorial:

===============
Getting Started
===============

This tutorial introduces :class:`~layered_config_tree.main.LayeredConfigTree`, a 
configuration data structure where values can be set at multiple priority layers. 
By default, reading a value returns the one from the highest-priority layer that 
has it defined.

Creating a Tree
===============

At its simplest, a tree can be created from a dictionary:

.. testcode::

    from layered_config_tree import LayeredConfigTree

    print(LayeredConfigTree({"greeting": "hello"}))

.. testoutput::

    greeting:
        base: hello

Note in the example above that by default a single `"base"` layer is used. You can 
also specify layers in order from lowest to highest priority:

.. testcode::

    tree = LayeredConfigTree(layers=["base", "override"])

We now have an empty tree with two layers, ``"base"`` and ``"override"``, where ``"override"``
has the higher priority (because it is later in the list of layers provided).

Adding Data
===========

Use :meth:`~layered_config_tree.main.LayeredConfigTree.update` to add data at a
specific layer. Data is provided as a (possibly nested) dictionary:

.. testcode::

    tree.update(
        {"name": "some_service", "database": {"host": "localhost", "port": 5432}},
        layer="base",
        source="defaults.yaml",
    )
    tree.update(
        {"database": {"host": "prod-server"}},
        layer="override",
        source="environment",
    )

The ``source`` parameter is optional metadata that records *where* a value came
from, which is useful for debugging.

In additional to providing data directly, you can initialize or update a tree from 
YAML strings or a path to a YAML file.

.. testcode::

    print(LayeredConfigTree("server:\n  host: localhost\n  port: 8080\n"))

.. testoutput::

    server:
        host:
            base: localhost
        port:
            base: 8080

Reading Values
==============

There are three ways to read from a ``LayeredConfigTree``, each with different behavior.

.. note::

    All three access methods can be chained together and/or mixed and matched as desired.

Dot access (``tree.key``)
-------------------------

Dot access returns the child of the highest-priority layer:

.. testcode::

    print(tree.name)            # leaf value
    print(tree.database)        # tree value

.. testoutput::

    some_service
    host:
        override: prod-server
    port:
        base: 5432

Notice that ``host`` returns ``"prod-server"`` (from the ``override`` layer), not
``"localhost"`` (from the ``base`` layer). The ``port`` value was only set at the
``base`` layer, so that value is returned.

A ``ConfigurationKeyError`` will be raised of the requested key does not exist at any layer.

get() method access
-------------------

:meth:`~layered_config_tree.main.LayeredConfigTree.get` works like :meth:`dict.get` 
and returns a default value (``None`` by default) when the key is missing instead of 
raising an error. It also accepts a list of keys for nested lookups and supports a 
``layer`` parameter to read from a specific layer:

.. testcode::

    print(tree.get("name"))                                 # same as dot access
    print(tree.get("missing"))                              # returns None
    print(tree.get("missing", default_value="fallback"))    # custom default
    print(tree.get(["database", "host"]))                   # nested lookup
    print(tree.database.get("host", layer="base"))          # specific layer

.. testoutput::

    some_service
    None
    fallback
    prod-server
    localhost

.. note::

    The interaction between ``default_value`` and ``layer`` may sometimes be a cause
    of confusion. The ``default_value`` at a requested ``layer`` will only be returned 
    *if the requested value does not exist at all*. If the requested value *does* exist - 
    just not at the requested layer - then you’ll get a ``MissingLayerError``.

    .. testcode::

        # url does not exist anywhere in the tree, so default_value is returned
        print(tree.get(["database", "url"], layer="override", default_value="missing"))

        # port exists at base layer but not override layer, so MissingLayerError is raised
        try:
             tree.get(["database", "port"], layer="override", default_value="missing")
        except Exception as e:
            print(type(e).__name__)

    .. testoutput::

        missing
        MissingLayerError
       
get_tree() method access
------------------------

:meth:`~layered_config_tree.main.LayeredConfigTree.get_tree` *guarantees* the result 
is a sub-tree and consists of all of the highest-priority values; it does *not*
support a ``layer`` argument or return a default value like :meth:`~layered_config_tree.main.LayeredConfigTree.get`.

.. testcode::

    print(tree.get_tree("database"))  # OK — returns a sub-tree

.. testoutput::

    host:
        override: prod-server
    port:
        base: 5432

If the value at the key path is a leaf, it raises ``ConfigurationError``:

.. testcode::

    try:
        tree.get_tree("name")
    except Exception as e:
        print(type(e).__name__)

.. testoutput::

    ConfigurationError

Printing a Tree
===============

Printing a tree (``str``) shows each value at its highest-priority layer:

.. testcode::

    print(tree)

.. testoutput::

    name:
        base: some_service
    database:
        host:
            override: prod-server
        port:
            base: 5432

Meanwhile, the ``repr`` shows *all* layers along with source information:

.. testcode::

    print(repr(tree))

.. testoutput::

    name:
        base: some_service
            source: defaults.yaml
    database:
        host:
            override: prod-server
                source: environment
            base: localhost
                source: defaults.yaml
        port:
            base: 5432
                source: defaults.yaml

Converting to a Dictionary
==========================

Use :meth:`~layered_config_tree.main.LayeredConfigTree.to_dict` to extract a plain
dictionary of highest priority information. 

.. testcode::

    print(tree.to_dict())

.. testoutput::

    {'name': 'some_service', 'database': {'host': 'prod-server', 'port': 5432}}

Note that all layer and source metadata is discarded.
