import pytest
import os
import tempfile
import threading
import time
from lib import lock


class TestLockBasics:
    def test_no_lock_flag_bypasses_locking(self):
        lock.no_lock_flag = True
        called = []
        def task():
            called.append(True)
            return "success"
        result = lock.control(lambda e: "error", True, "/nonexistent.lck", task)
        assert result == "success"
        assert called == [True]
        lock.no_lock_flag = False

    def test_dotlck_filename_bypasses_locking(self):
        called = []
        def task():
            called.append(True)
            return "done"
        result = lock.control(lambda e: "error", True, ".lck", task)
        assert result == "done"
        assert called == [True]

    def test_successful_lock_and_execute(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            lock_file = tf.name
        try:
            result = lock.control(
                lambda e: f"error: {e}",
                True,
                lock_file,
                lambda: "executed"
            )
            assert result == "executed"
        finally:
            try:
                os.unlink(lock_file)
            except:
                pass

    def test_lock_file_created_if_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_file = os.path.join(tmpdir, "test.lck")
            assert not os.path.exists(lock_file)
            lock.control(lambda e: None, True, lock_file, lambda: None)
            assert os.path.exists(lock_file)


class TestLockWaiting:
    def test_wait_mode_blocks_until_released(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            lock_file = tf.name
        try:
            results = []
            def holder():
                lock.control(
                    lambda e: None,
                    True,
                    lock_file,
                    lambda: (time.sleep(0.3), results.append("holder"))[-1]
                )
            def waiter():
                time.sleep(0.1)
                lock.control(
                    lambda e: None,
                    True,
                    lock_file,
                    lambda: results.append("waiter")
                )
            t1 = threading.Thread(target=holder)
            t2 = threading.Thread(target=waiter)
            t1.start()
            t2.start()
            t1.join(timeout=2)
            t2.join(timeout=2)
            assert len(results) == 2
            assert "holder" in results
            assert "waiter" in results
        finally:
            try:
                os.unlink(lock_file)
            except:
                pass


class TestExceptionHandling:
    def test_on_exn_called_on_acquire_failure(self):
        pytest.skip("Platform-dependent lock behavior - skipping for now")

    def test_exception_in_task_propagates(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            lock_file = tf.name
        try:
            def failing_task():
                raise ValueError("task failed")
            with pytest.raises(ValueError, match="task failed"):
                lock.control(lambda e: None, True, lock_file, failing_task)
        finally:
            try:
                os.unlink(lock_file)
            except:
                pass

    def test_lock_released_on_exception(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            lock_file = tf.name
        try:
            def failing_task():
                raise RuntimeError("oops")
            with pytest.raises(RuntimeError):
                lock.control(lambda e: None, True, lock_file, failing_task)
            result = lock.control(lambda e: "error", True, lock_file, lambda: "success")
            assert result == "success"
        finally:
            try:
                os.unlink(lock_file)
            except:
                pass


class TestPpException:
    def test_exception_formatting(self):
        try:
            raise ValueError("test error")
        except Exception as e:
            result = lock.pp_exception(e)
            assert "ValueError" in result
            assert "test error" in result
