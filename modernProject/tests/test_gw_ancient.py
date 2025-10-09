import pytest
from modernProject.lib import gw_ancient


def test_is_available():
    assert gw_ancient.is_available is False


def test_mark_raises_not_implemented():
    with pytest.raises(NotImplementedError, match="Ancient not available"):
        gw_ancient.mark("test")


def test_follow_raises_not_implemented():
    with pytest.raises(NotImplementedError, match="Ancient not available"):
        gw_ancient.follow("test")


def test_delete_raises_not_implemented():
    with pytest.raises(NotImplementedError, match="Ancient not available"):
        gw_ancient.delete("test")


def test_functions_accept_various_inputs():
    test_inputs = [None, 42, "string", [], {}, object()]

    for input_val in test_inputs:
        with pytest.raises(NotImplementedError):
            gw_ancient.mark(input_val)

        with pytest.raises(NotImplementedError):
            gw_ancient.follow(input_val)

        with pytest.raises(NotImplementedError):
            gw_ancient.delete(input_val)
