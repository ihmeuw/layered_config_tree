"""Shim release.

``layered_config_tree`` has been renamed to ``vivarium-config-tree`` and now lives in the
``vivarium-suite`` monorepo at ``libs/config-tree/``. This release ships no Python code;
it exists only so ``pip install layered_config_tree`` transparently installs the
``vivarium-config-tree`` package. See README.rst.
"""

from pathlib import Path

from setuptools import setup

long_description = (Path(__file__).parent / "README.rst").read_text()

setup(
    name="layered_config_tree",
    description="Renamed to vivarium-config-tree; this package is a redirect. See README.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    install_requires=["vivarium-config-tree>=5.0.0"],
    packages=[],
    py_modules=[],
    use_scm_version={
        "tag_regex": r"^(?P<prefix>v)?(?P<version>[^\+]+)(?P<suffix>.*)?$",
    },
    setup_requires=["setuptools_scm"],
)
