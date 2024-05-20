from typing import Mapping, TypeAlias, Union

# Define a nested dictionary of unknown depth for type hinting
NestedDict: TypeAlias = Mapping[str, "NestedDictValue"]
# NOTE: We need to skip return-value checks for the following NestedDictValue
# because it's a recursive type alias with NestedDict.
NestedDictValue: TypeAlias = Union[
    str, int, float, bool, list[Union[str, int, float]], NestedDict
]
