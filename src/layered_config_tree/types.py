from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from layered_config_tree import LayeredConfigTree

# Data input types
InputData = Union[dict[str, Any], str, Path, "LayeredConfigTree"]
