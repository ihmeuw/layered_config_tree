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
