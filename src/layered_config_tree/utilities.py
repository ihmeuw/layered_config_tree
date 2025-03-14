"""
=========
Utilities
=========

This module contains utility functions and classes for the layered_config_tree
package.

"""

from collections.abc import Hashable
from pathlib import Path
from typing import Any

import yaml

from layered_config_tree import DuplicatedConfigurationError


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

    def __init__(self, *args, **kwargs):
        """Initialize the SafeLoader with an empty `path` list."""
        super().__init__(*args, **kwargs)
        self.path = []

    def construct_mapping(
        self,
        node: yaml.MappingNode,
        deep: bool = False,
    ) -> dict[Hashable, Any]:
        """Constructs the standard mapping after checking for duplicates.

        This is a custom implementation of the `construct_mapping` method from
        the `yaml.SafeLoader` class. It is designed to construct a standard
        Python mapping (dictionary) from a YAML mapping node while enforcing
        the constraint that duplicate keys within a given level results in an
        error being raised.

        Parameters
        ----------
        node
            The YAML mapping node to construct.
        deep
            Whether or not to recursively construct mappings.

        Raises
        ------
        DuplicateKeysInYAMLError
            If duplicate keys within the same level are detected in the YAML file
            being loaded.

        Notes
        -----
        A key is considered a duplicate only if it is at the same level as the other
        key of the same name; any number of keys can have the same value as long as
        they are all at different levels in the hierarchy.

        This raises upon the _first_ duplicate key found; other duplicates may exist.

        """

        if not isinstance(node, yaml.MappingNode):
            raise yaml.constructor.ConstructorError(
                None, None, "expected a mapping node, but found %s" % node.id, node.start_mark
            )
        self.flatten_mapping(node)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                full_path = "-".join(self.path + [key])
                raise DuplicatedConfigurationError(
                    f"Duplicate key(s) detected in YAML file being loaded: {full_path}",
                    name=f"duplicated_{key}",
                    layer=None,
                    source=None,
                    value=None,
                )
            if not isinstance(key, Hashable):
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found unhashable key",
                    key_node.start_mark,
                )
            self.path.append(key)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
            self.path.pop()
        return mapping

    def construct_object(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            # For mapping nodes, manage the path directly in construct_mapping
            return self.construct_mapping(node, deep=deep)
        elif isinstance(node, yaml.SequenceNode):
            # For sequence nodes, handle each item without altering the path
            return [self.construct_object(child, deep) for child in node.value]
        else:
            # For scalar nodes, simply return the value without path manipulation
            return super().construct_object(node, deep=deep)
