from typing import Mapping, Union

# NOTE: py 3.9 does not support typing.TypeAlias
# Define a nested dictionary of unknown depth for type hinting
NestedDict = Mapping[str, "NestedDictValue"]
# Define the leaf (ConfigNode) values (which cannot be another dictionary)
ConfigNodeValue = Union[str, int, float, list[Union[str, int, float]]]
# Define a NestedDictionary value which can be either a ConfigNodeValue or another NestedDict
# NOTE: Due to the forward reference to NestedDictValue above, static type checkers
#   (e.g. mypy) may not be able to determine the correct type of NestedDictValue;
#   use # type: ignore as required
NestedDictValue = Union[ConfigNodeValue, NestedDict]
