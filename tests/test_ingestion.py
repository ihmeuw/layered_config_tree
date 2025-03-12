from pathlib import Path

import pytest

from layered_config_tree import LayeredConfigTree

TEST_YAML_ONE = """
test_section:
    test_key: test_value
    test_key2: test_value2
test_section2:
    test_key: test_value3
    test_key2: test_value4
"""


def test_load_yaml_string() -> None:
    lct = LayeredConfigTree()
    lct.update(TEST_YAML_ONE, source="inline_test")

    assert lct.test_section.test_key == "test_value"
    assert lct.test_section.test_key2 == "test_value2"
    assert lct.test_section2.test_key == "test_value3"


@pytest.mark.parametrize("path_type", [str, Path])
def test_load_yaml_file(tmp_path: Path, path_type: type[str | Path]) -> None:
    tmp_file = tmp_path / "test_file.yaml"
    tmp_file.write_text(TEST_YAML_ONE)

    lct = LayeredConfigTree()
    filepath_to_test = str(tmp_file) if path_type is str else tmp_file
    lct.update(filepath_to_test)

    assert lct.test_section.test_key == "test_value"
    assert lct.test_section.test_key2 == "test_value2"
    assert lct.test_section2.test_key == "test_value3"
