import re
import sys

import pytest


def test_python_version_satisfies_project_requirement() -> None:
    assert sys.version_info >= (3, 13)


def test_pytest_version_is_latest_stable_major_range() -> None:
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", pytest.__version__)
    assert match is not None

    version = tuple(int(part) for part in match.groups())
    assert (9, 1, 1) <= version < (10, 0, 0)
