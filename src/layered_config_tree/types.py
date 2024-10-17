from pathlib import Path
from typing import TYPE_CHECKING, Any, Mapping, Union

if TYPE_CHECKING:
    from layered_config_tree import LayeredConfigTree


# NOTE: py 3.9 does not support typing.TypeAlias

# Define a nested dictionary of unknown depth for type hinting
NestedDict = Mapping[str, Any]

# Data input types
InputData = Union[NestedDict, str, Path, "LayeredConfigTree"]
