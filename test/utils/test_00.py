import os

import pytest

from backend import utils


def test_00(capfd: pytest.CaptureFixture[str]) -> None:
    utils.test()
    out, err = capfd.readouterr()
    assert "This is a test!" + os.linesep == out
    assert "" == err
