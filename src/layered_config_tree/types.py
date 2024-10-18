from __future__ import annotations

from pathlib import Path
from typing import Any, Union

# Data input types
InputData = Union[dict[str, Any], str, Path, "LayeredConfigTree"]
