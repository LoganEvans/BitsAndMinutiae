import threading
import copy
import time

class XetumWriteException(Exception):
    pass


class _XetumSingleton(object):
    def __init__(self, to_wrap):
        self.lock = threading.Semaphore(value=1)
        self.wrapped = to_wrap
        self.version = 1

    def read(self):
        # The version must match the data.
        with self.lock:
            return self.wrapped, self.version

    def write(self, new_value, version):
        # Phase one. Prepare data.
        wrapped_next = copy.deepcopy(new_value)

        # Phase two. Commit data.
        with self.lock:
            if version == self.version:
                self.wrapped = wrapped_next
                self.version += 1
            else:
                raise XetumWriteException()


class Xetum(object):
    """This defines a wrapper for an object shared by multiple threads.

    Xetum is muteX backward.

    This idea is this: A mutex prevents multiple threads from working on data
    at the same time. This can lead to low CPU utilization if the other threads
    have nothing else to do. A backward approach is to allow all threads to
    attempt to do work. When it comes time to save that work, the Xetum will
    perform a two phase write. In the first phase, it copies the new value. On
    the second phase, it grabs a mutex, checks to make sure the version numbers
    for the data are correct, and if they are, commits the change. If the
    version numbers aren't correct, the thread must catch a XetumWriteException
    and try again. The intention is to minimize the amount of time the mutex is
    locked.

    """
    def __init__(self, to_wrap):
        if not isinstance(to_wrap, Xetum):
            self.xetum_singleton = _XetumSingleton(to_wrap)
            self.version = None
        else:
            # The version must match the data.
            with to_wrap.xetum_singleton.lock:
                self.xetum_singleton = to_wrap.xetum_singleton
                self.version = to_wrap.version

    @property
    def data(self):
        self.value, self.version = self.xetum_singleton.read()
        return self.value

    @data.setter
    def data(self, new_value):
        self.xetum_singleton.write(new_value, self.version)


if __name__ == '__main__':
    def test_xetum(shared_value, sleep_time, remaining):
        local_value = Xetum(shared_value)
        while remaining:
            try:
                next_value = local_value.data + 1
                # Let's simulate some kind of work load (and force some starvation)
                time.sleep(sleep_time)
                local_value.data = next_value
                remaining -= 1
                print local_value.data, "written by", threading.currentThread().name
            except XetumWriteException:
                print "    {name} failed to write {value}".format(
                        name=threading.currentThread().name,
                        value=next_value)
    threads = []
    shared_value = Xetum(0)
    # These times and quotas are chosen so that they (probably) will produce
    # consistent results.
    sleep_times = (0.03, 0.05, 0.07)
    quotas = (4, 3, 2)
    for i, (sleep_time, quota) in enumerate(zip(sleep_times, quotas)):
        threads.append(threading.Thread(
                target=test_xetum,
                args=(shared_value, sleep_time, quota)))
    for thread in threads:
        thread.start()

    expected_result = """
1 written by Thread-1
    Thread-2 failed to write 1
2 written by Thread-1
    Thread-3 failed to write 1
3 written by Thread-1
    Thread-2 failed to write 2
4 written by Thread-1
    Thread-3 failed to write 3
    Thread-2 failed to write 4
5 written by Thread-2
    Thread-3 failed to write 5
6 written by Thread-2
    Thread-3 failed to write 6
7 written by Thread-2
    Thread-3 failed to write 7
8 written by Thread-3
9 written by Thread-3
        """

