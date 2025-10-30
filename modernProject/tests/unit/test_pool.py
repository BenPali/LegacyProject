import pytest
from lib.pool import Pool


def test_pool_creation():
    pool = Pool()
    assert pool.max_workers == 10
    assert pool.workers == []


def test_pool_custom_max_workers():
    pool = Pool(max_workers=5)
    assert pool.max_workers == 5


def test_pool_submit_simple_function():
    pool = Pool()

    def add(a, b):
        return a + b

    result = pool.submit(add, 2, 3)
    assert result == 5


def test_pool_submit_with_kwargs():
    pool = Pool()

    def greet(name, greeting="Hello"):
        return f"{greeting}, {name}!"

    result = pool.submit(greet, "Alice", greeting="Hi")
    assert result == "Hi, Alice!"


def test_pool_submit_no_args():
    pool = Pool()

    def get_value():
        return 42

    result = pool.submit(get_value)
    assert result == 42


def test_pool_submit_multiple_tasks():
    pool = Pool()

    def multiply(x):
        return x * 2

    results = []
    for i in range(5):
        result = pool.submit(multiply, i)
        results.append(result)

    assert results == [0, 2, 4, 6, 8]


def test_pool_shutdown():
    pool = Pool()
    pool.workers = [1, 2, 3]
    pool.shutdown()
    assert pool.workers == []


def test_pool_submit_lambda():
    pool = Pool()
    result = pool.submit(lambda x: x ** 2, 4)
    assert result == 16


def test_pool_submit_with_exception():
    pool = Pool()

    def failing_function():
        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        pool.submit(failing_function)
