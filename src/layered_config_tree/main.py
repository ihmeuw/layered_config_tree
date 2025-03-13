"""
===================
Layered Config Tree
===================

A configuration structure that supports cascading layers.

Layered Config Tree allows base configurations to be overridden by multiple layers with
cascading priorities. The configuration values are presented as attributes of the
configuration object and are the value of the keys in the outermost layer of
configuration where they appear.

For example:

.. code-block:: python

    >>> config = LayeredConfigTree(layers=['inner_layer', 'middle_layer', 'outer_layer', 'user_overrides'])
    >>> config.update({'section_a': {'item1': 'value1', 'item2': 'value2'}, 'section_b': {'item1': 'value3'}}, layer='inner_layer')
    >>> config.update({'section_a': {'item1': 'value4'}, 'section_b': {'item1': 'value5'}}, layer='middle_layer')
    >>> config.update({'section_b': {'item1': 'value6'}}, layer='outer_layer')
    >>> config.section_a.item1
    'value4'
    >>> config.section_a.item2
    'value2'
    >>> config.section_b.item1
    'value6'

"""

from __future__ import annotations

from collections.abc import Hashable, Iterable
from pathlib import Path
from typing import Any

import yaml

from layered_config_tree import (
    ConfigurationError,
    ConfigurationKeyError,
    DuplicatedConfigurationError,
    ImproperAccessError,
)
from layered_config_tree.types import InputData


class ConfigNode:
    """A priority based configuration value.

    A :class:`ConfigNode` represents a single configuration value with
    priority-based layers.  The intent is to allow a value to be set from
    sources with different priorities and to record what the value was set
    to and from where.

    For example, a simulation may need certain values to always exist, and so
    it will set them up at a "base" layer. Components in the simulation may
    have a different set of priorities and so override the "base" value at
    a "component" level.  Finally a user may want to override the simulation
    and component defaults with values at the command line or interactively,
    and so those values will be set in a final "user" layer.

    A :class:`ConfigNode` may only have a value set at each layer once.
    Attempts to set a value at the same layer multiple times will result in
    a :class:`DuplicatedConfigurationError`.

    The :class:`ConfigNode` will record all values set and the source they
    are set from.  This sort of provenance with configuration data greatly
    eases debugging and analysis of simulation code.

    This class should not be instantiated directly. All interaction should
    take place by manipulating a :class:`LayeredConfigTree` object.

    """

    def __init__(self, layers: list[str], name: str):
        self._name = name
        self._layers = layers
        self._values: dict[str, tuple[str | None, Any]] = {}
        self._frozen = False
        self._accessed = False

    @property
    def name(self) -> str:
        """The name of this configuration value."""
        return self._name

    @property
    def accessed(self) -> bool:
        """Returns whether this node has been accessed."""
        return self._accessed

    @property
    def metadata(self) -> list[dict[str, Any | str | None]]:
        """Returns all values and associated metadata for this node."""
        result = []
        for layer in self._layers:
            if layer in self._values:
                result.append(
                    {
                        "layer": layer,
                        "source": self._values[layer][0],
                        "value": self._values[layer][1],
                    }
                )
        return result

    def freeze(self) -> None:
        """Causes the :class:`ConfigNode` node to become read only.

        This can be used to create a contract around when the configuration is
        modifiable.

        """
        self._frozen = True

    def get_value(self, layer: str | None = None) -> Any:
        """Returns the value at the specified layer.

        If no layer is specified, the outermost (highest priority) layer
        at which a value has been set will be used.

        Parameters
        ----------
        layer
            Name of the layer to retrieve the value from.

        Raises
        ------
        KeyError
            If no value has been set at any layer.

        """
        value = self._get_value_with_source(layer)[1]
        self._accessed = True
        return value

    def update(self, value: Any, layer: str | None, source: str | None) -> None:
        """Set a value for a layer with optional metadata about source.

        Parameters
        ----------
        value
            Data to store in the node.
        layer
            Name of the layer to use. If no layer is provided, the value will
            be set in the outermost (highest priority) layer.
        source
            Metadata indicating the source of this value.

        Raises
        ------
        ConfigurationError
            If the node is frozen.
        ConfigurationKeyError
            If the provided layer does not exist.
        DuplicatedConfigurationError
            If a value has already been set at the provided layer or a value
            is already in the outermost layer and no layer has been provided.

        """
        if self._frozen:
            raise ConfigurationError(
                f"Frozen ConfigNode {self.name} does not support assignment.", self.name
            )

        layer = layer if layer else self._layers[-1]

        if layer not in self._layers:
            raise ConfigurationKeyError(
                f"No layer {layer} in ConfigNode {self.name}.", self.name
            )
        elif layer in self._values:
            source, value = self._values[layer]
            raise DuplicatedConfigurationError(
                f"Value has already been set at layer {layer}.",
                name=self.name,
                layer=layer,
                source=source,
                value=value,
            )
        else:
            self._values[layer] = (source, value)

    def _get_value_with_source(self, layer: str | None) -> tuple[str | None, Any]:
        """Returns a (source, value) tuple at the specified layer.

        If no layer is specified, the outermost (highest priority) layer
        at which a value has been set will be used.

        Parameters
        ----------
        layer
            Name of the layer to retrieve the (source, value) pair from.

        Raises
        ------
        KeyError
            If no value has been set at any layer.

        """
        if layer and layer in self._values:
            return self._values[layer]

        for layer in reversed(self._layers):
            if layer in self._values:
                return self._values[layer]

        raise ConfigurationKeyError(
            f"No value stored in this ConfigNode {self.name}.", self.name
        )

    def __bool__(self) -> bool:
        return bool(self._values)

    def __repr__(self) -> str:
        out = []
        for m in reversed(self.metadata):
            layer, source, value = m.values()
            out.append(f"{layer}: {value}\n    source: {source}")
        return "\n".join(out)

    def __str__(self) -> str:
        if not self:
            return ""
        layer, _, value = self.metadata[-1].values()
        return f"{layer}: {value}"


class ConfigIterator:
    """
    An iterator for a LayeredConfigTree object.

    This iterator is used to iterate over the keys of a LayeredConfigTree object.
    """

    def __init__(self, config_tree: LayeredConfigTree):
        self._iterator = iter(config_tree._children)

    def __iter__(self) -> ConfigIterator:
        return self

    def __next__(self) -> str:
        return next(self._iterator)


class LayeredConfigTree:
    """A container for configuration information.

    Each configuration value is exposed as an attribute the value of which
    is determined by the outermost layer which has the key defined.

    """

    # Define type annotations here since they're indirectly defined below
    _layers: list[str]
    _children: dict[str, LayeredConfigTree | ConfigNode]
    _frozen: bool
    _name: str

    def __init__(
        self,
        data: InputData | None = None,
        layers: list[str] = [],
        name: str = "",
    ):
        """
        Parameters
        ----------
        data
            The :class:`LayeredConfigTree` accepts many kinds of data:

             - :class:`dict` : Flat or nested dictionaries may be provided.
               Keys of dictionaries at all levels must be strings.
             - :class:`LayeredConfigTree` : Another :class:`LayeredConfigTree` can be
               used. All source information will be ignored and the source
               will be set to 'initial_data' and values will be stored at
               the lowest priority level.
             - :class:`str` : Strings provided can be yaml formatted strings,
               which will be parsed into a dictionary using standard yaml
               parsing. Alternatively, a path to a yaml file may be provided
               and the file will be read in and parsed.
             - :class:`pathlib.Path` : A path object to a yaml file will
               be interpreted the same as a string representation.

            All values will be set with 'initial_data' as the source and
            will use the lowest priority level. If values are set at higher
            priorities they will be used when the :class:`LayeredConfigTree` is
            accessed.
        layers
            A list of layer names. The order in which layers defined
            determines their priority.  Later layers override the values from
            earlier ones.

        """
        self.__dict__["_layers"] = layers if layers else ["base"]
        self.__dict__["_children"] = {}
        self.__dict__["_frozen"] = False
        self.__dict__["_name"] = name
        self.update(data, layer=self._layers[0], source="initial data")

    def freeze(self) -> None:
        """Causes the LayeredConfigTree to become read only.

        This is useful for loading and then freezing configurations that
        should not be modified at runtime.

        """
        self.__dict__["_frozen"] = True
        for child in self.values():
            child.freeze()

    def items(self) -> Iterable[tuple[str, LayeredConfigTree | ConfigNode]]:
        """Return an iterable of all (child_name, child) pairs."""
        return self._children.items()

    def keys(self) -> Iterable[str]:
        """Return an Iterable of all child names."""
        return self._children.keys()

    def values(self) -> Iterable[LayeredConfigTree | ConfigNode]:
        """Return an Iterable of all children."""
        return self._children.values()

    def unused_keys(self) -> list[str]:
        """Lists all values in the LayeredConfigTree that haven't been accessed."""
        unused = []
        for name, child in self.items():
            if isinstance(child, ConfigNode):
                if not child.accessed:
                    unused.append(name)
            else:
                for grandchild_name in child.unused_keys():
                    unused.append(f"{name}.{grandchild_name}")
        return unused

    def to_dict(self) -> dict[str, Any]:
        """Converts the LayeredConfigTree into a nested dictionary.

        All metadata is lost in this conversion.

        """
        result = {}
        for name, child in self.items():
            if isinstance(child, ConfigNode):
                result[name] = child.get_value(layer=None)
            else:
                result[name] = child.to_dict()
        return result

    def get(self, key: str, default_value: Any = None) -> Any:
        """Return the LayeredConfigTree or value at the key in the outermost layer of the config tree.

        Parameters
        ----------
        key
            The string to look for in the outermost layer of the config tree.
        default_value
            The value to return if key is not found
        """
        return self[key] if key in self._children else default_value

    def get_tree(self, key: str) -> LayeredConfigTree:
        """Return the LayeredConfigTree at the key in the outermost layer of the config tree.

        Parameters
        ----------
        key
            The str we look up in the outermost layer of the config tree.
        """
        data = self[key]
        if isinstance(data, LayeredConfigTree):
            return data
        else:
            raise ConfigurationError(
                f"The data you accessed using {key} with get_tree was of type {type(data)}, but get_tree must return a LayeredConfigTree."
            )

    def get_from_layer(self, name: str, layer: str | None = None) -> Any:
        """Get a configuration value from the provided layer.

        If no layer is specified, the outermost (highest priority) layer
        at which a value has been set will be used.

        Parameters
        ----------
        name
            The name of the value to retrieve
        layer
            The name of the layer to retrieve the value from.

        """
        if name not in self:
            name = f"{self._name}.{name}" if self._name else name
            raise ConfigurationKeyError(f"No value at name {name}.", name)

        child = self._children[name]
        if isinstance(child, ConfigNode):
            return child.get_value(layer)
        else:
            return child

    def update(
        self,
        data: InputData | None,
        layer: str | None = None,
        source: str | None = None,
    ) -> None:
        """Adds additional data into the :class:`LayeredConfigTree`.

        Parameters
        ----------
        data
            :func:`~LayeredConfigTree.update` accepts many types of data.

             - :class:`dict` : Flat or nested dictionaries may be provided.
               Keys of dictionaries at all levels must be strings.
             - :class:`str` : Strings provided can be yaml formatted strings,
               which will be parsed into a dictionary using standard yaml
               parsing. Alternatively, a path to a yaml file may be provided
               and the file will be read in and parsed.
             - :class:`pathlib.Path` : A path object to a yaml file will
               be interpreted the same as a string representation.
             - :class:`LayeredConfigTree` : Another :class:`LayeredConfigTree` can be
               used. All source information will be ignored and the
               provided layer and source will be used to set the metadata.
        layer
            The name of the layer to store the value in.  If no layer is
            provided, the value will be set in the outermost (highest priority)
            layer.
        source
            The source to attribute the value to.

        Raises
        ------
        ConfigurationError
            If the :class:`LayeredConfigTree` is frozen or attempting to assign
            an invalid value.
        ConfigurationKeyError
            If the provided layer does not exist.
        DuplicatedConfigurationError
            If a value has already been set at the provided layer or a value
            is already in the outermost layer and no layer has been provided.

        """
        if data is not None:
            data_dict, source = self._coerce(data, source)
            for k, v in data_dict.items():
                self._set_with_metadata(k, v, layer, source)

    def metadata(self, name: str) -> list[dict[str, Any]]:
        if name in self:
            return self._children[name].metadata  # type: ignore[return-value]
        name = f"{self._name}.{name}" if self._name else name
        raise ConfigurationKeyError(f"No configuration value with name {name}", name)

    @staticmethod
    def _coerce(
        data: InputData,
        source: str | None,
    ) -> tuple[dict[str, Any], str | None]:
        """Coerces data into dictionary format."""
        if isinstance(data, dict):
            return data, source
        elif (isinstance(data, str) and data.endswith((".yaml", ".yml"))) or isinstance(
            data, Path
        ):
            # 'data' is a filepath to a yaml file
            source = source if source else str(data)
            coerced_data = load_yaml(data)
            if not isinstance(coerced_data, dict):
                raise ValueError(
                    f"Loaded yaml file {coerced_data} should be a dictionary but is type {type(coerced_data)}"
                )
            return coerced_data, source
        elif isinstance(data, str):
            # 'data' is a yaml string
            data = load_yaml(data)
            if not isinstance(data, dict):
                raise ValueError(
                    f"Loaded yaml file {data} should be a dictionary but is type {type(data)}"
                )
            return data, source
        elif isinstance(data, LayeredConfigTree):
            return data.to_dict(), source
        else:
            raise ConfigurationError(
                f"LayeredConfigTree can only update from dictionaries, strings, paths and LayeredConfigTrees. "
                f"You passed in {type(data)}",
                value_name=None,
            )

    def _set_with_metadata(
        self,
        name: str,
        value: Any,
        layer: str | None,
        source: str | None,
    ) -> None:
        """Set a value in the named layer with the given source.

        Parameters
        ----------
        name
            The name of the value.
        value
            The value to store.
        layer
            The name of the layer to store the value in.  If no layer is
            provided, the value will be set in the outermost (highest priority)
            layer.
        source
            The source to attribute the value to.

        Raises
        ------
        ConfigurationError
            If the :class:`LayeredConfigTree` is frozen or attempting to assign
            an invalid value.
        ConfigurationKeyError
            If the provided layer does not exist.
        DuplicatedConfigurationError
            If a value has already been set at the provided layer or a value
            is already in the outermost layer and no layer has been provided.

        """
        if self._frozen:
            raise ConfigurationError(
                f"Frozen LayeredConfigTree {self._name} does not support assignment.",
                self._name,
            )

        if isinstance(value, dict):
            if name not in self:
                self._children[name] = LayeredConfigTree(layers=list(self._layers), name=name)
            if isinstance(self._children[name], ConfigNode):
                name = f"{self._name}.{name}" if self._name else name
                raise ConfigurationError(
                    f"Can't assign a dictionary as a value to a ConfigNode.", name
                )
        else:
            if name not in self:
                self._children[name] = ConfigNode(list(self._layers), name=self._name)
            if isinstance(self._children[name], LayeredConfigTree):
                name = f"{self._name}.{name}" if self._name else name
                raise ConfigurationError(
                    f"Can't assign a value to a LayeredConfigTree.", name
                )

        self._children[name].update(value, layer, source)

    def __setattr__(self, name: str, value: Any) -> None:
        """Set a value on the outermost layer.

        Notes
        -----
        We allow keys that look like dunder attributes, i.e. start and end with
        "__". However, to avoid conflict with actual dunder methods and attributes,
        we do not allow setting them via this method and instead require dictionary
        access (i.e. bracket notation).
        """
        if name not in self:
            raise ConfigurationKeyError(
                "New configuration keys can only be created with the update method.",
                self._name,
            )
        if name.startswith("__") and name.endswith("__"):
            raise ImproperAccessError(
                "Cannot set an attribute starting and ending with '__' via attribute "
                "access (i.e. dot notation). Use dictionary access instead "
                "(i.e. bracket notation)."
            )
        self._set_with_metadata(name, value, layer=None, source=None)

    def __setitem__(self, name: str, value: Any) -> None:
        """Set a value on the outermost layer."""
        if name not in self:
            raise ConfigurationKeyError(
                "New configuration keys can only be created with the update method.",
                self._name,
            )
        self._set_with_metadata(name, value, layer=None, source=None)

    # FIXME: We expect the return to be a ConfigNode or LayeredConfigTree but
    # static type checkers don't know what you're getting back in chained
    # attribute calls. We type hint returning Any as a workaround.
    def __getattr__(self, name: str) -> Any:
        """Get a value from the outermost layer in which it appears.

        Notes
        -----
        We allow keys that look like dunder attributes, i.e. start and end with
        "__". However, to avoid conflict with actual dunder methods and attributes,
        we do not allow getting them via this method and instead require dictionary
        access (i.e. bracket notation).

        If the requested attribute starts and ends with "__" but *does not* actually
        exist, it is critical that we raise an AttributeError since some functions
        specifically handle it, e.g. ``pickle`` and ``copy.deepcopy``.
        See https://stackoverflow.com/a/50888571/

        One the other hand, if the requested attribute starts and ends with "__"
        and *does* exist, it is critical that we raise a non-AttributeError exception
        so as not to conflict with dunder methods and attributes.
        """
        if name.startswith("__") and name.endswith("__"):
            if name not in self:
                raise AttributeError  # Do not change from AttributeError
            raise ImproperAccessError(
                "Cannot get an attribute starting and ending with '__' via attribute "
                "access (i.e. dot notation). Use dictionary access instead "
                "(i.e. bracket notation)."
            )
        return self.get_from_layer(name)

    # We need custom definitions of __getstate__ and __setstate__
    # because of our custom attribute getters/setters.
    # Specifically:
    # * The pickle module will invoke our __getattr__ checking for __getstate__
    #   and __setstate__, and only catch AttributeError (not ConfigurationKeyError), and
    # * Calling __getattr__ before we have set up the state doesn't work,
    #   because it leads to an infinite loop looking for the module's
    #   actual attributes (not config keys)
    def __getstate__(self) -> dict[str, Any]:
        return self.__dict__

    def __setstate__(self, state: dict[str, Any]) -> None:
        for k, v in state.items():
            self.__dict__[k] = v

    def __getitem__(self, name: str) -> Any:
        """Get a value from the outermost layer in which it appears."""
        return self.get_from_layer(name)

    def __delattr__(self, name: str) -> None:
        if name in self:
            del self._children[name]

    def __delitem__(self, name: str) -> None:
        if name in self:
            del self._children[name]

    def __contains__(self, name: str) -> bool:
        """Test if a configuration key exists in any layer."""
        return name in self._children

    def __iter__(self) -> ConfigIterator:
        """Dictionary-like iteration."""
        return ConfigIterator(self)

    def __len__(self) -> int:
        return len(self._children)

    def __dir__(self) -> list[str]:
        return list(self._children.keys()) + dir(super(LayeredConfigTree, self))

    def __repr__(self) -> str:
        return "\n".join(
            [
                "{}:\n    {}".format(name, repr(c).replace("\n", "\n    "))
                for name, c in self._children.items()
            ]
        )

    def __str__(self) -> str:
        return "\n".join(
            [
                "{}:\n    {}".format(name, str(c).replace("\n", "\n    "))
                for name, c in self._children.items()
            ]
        )

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError


def load_yaml(data: str | Path) -> dict[str, Any]:
    """Loads a YAML filepath or string into a dictionary.

    Parameters
    ----------
    data
        The YAML content to load. This can be a file path to a YAML file or a string
        containing YAML-formatted text.

    Returns
    -------
        A dictionary representation of the loaded YAML content.

    Notes
    -----
    If `data` is a Path object or a string that ends with ".yaml" or ".yml", it is
    treated as a filepath and this function loads the file. Otherwise, `data` is a
    string that does _not_ end in ".yaml" or ".yml" and it is treated as YAML-formatted
    text which is loaded directly into a dictionary.
    """

    data_dict: dict[str, Any]
    if (isinstance(data, str) and data.endswith((".yaml", ".yml"))) or isinstance(data, Path):
        # 'data' is a filepath to a yaml file
        with open(data) as f:
            data_file = f.read()
        data_dict = yaml.load(data_file, Loader=SafeLoader)
    else:
        # 'data' is a yaml string
        data_dict = yaml.load(data, Loader=SafeLoader)
    return data_dict


class SafeLoader(yaml.SafeLoader):
    """A yaml.SafeLoader that restricts duplicate keys."""

    def construct_mapping(
        self,
        node: yaml.MappingNode,
        deep: bool = False,
        path: list[str] | None = None,
    ) -> dict[Hashable, Any]:
        """Constructs the standard mapping after checking for duplicates.

        Parameters
        ----------
        node
            The YAML mapping node to construct.
        deep
            Whether or not to recursively construct mappings.
        path
            The path to the current node in the YAML document.

        Raises
        ------
        DuplicateKeysInYAMLError
            If duplicate keys within the same level are detected in the YAML file
            being loaded.

        Notes
        -----
        The duplicate key check is performed _only at the level of the mapping being
        currently constructed_. This means that if the YAML document contains nested
        mappings, each mapping is checked independently for duplicates. As a result,
        fixing a duplicate in one level of the document will not prevent this method
        from raising an error for duplicates in another upon subsequent loads.
        """
        path = [] if path is None else path
        seen = set()
        duplicates = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)  # type: ignore[no-untyped-call]
            full_path = path + [key]
            if key in seen:
                duplicates[key] = full_path
            else:
                seen.add(key)
            # update path
            if isinstance(value_node, yaml.MappingNode):
                self.construct_mapping(value_node, deep, full_path)
        if duplicates:
            formatted_duplicates = "\n".join(
                [f"* {'-'.join(map(str, v))}" for v in duplicates.values()]
            )
            raise DuplicatedConfigurationError(
                f"Duplicate key(s) detected in YAML file being loaded:\n{formatted_duplicates}",
                name=f"duplicates_{'_'.join(duplicates)}",
                layer=None,
                source=None,
                value=None,
            )
        return super().construct_mapping(node, deep)
