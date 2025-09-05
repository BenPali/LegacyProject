import pytest
from main import hello

def test_hello():
    assert hello() == "Hello World!"

def test_main_execution(capsys):
    from main import hello
    print(hello())
    captured = capsys.readouterr()
    assert captured.out == "Hello World!\n"