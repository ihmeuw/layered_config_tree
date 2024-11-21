from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from layered_config_tree import LayeredConfigTree

# Data input types
InputData = TypeVar("InputData", dict[str, Any], str, Path, "LayeredConfigTree")
