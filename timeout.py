import sys
import trace
import threading
import Queue
import time

class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill() method.

    Source for class:
    https://mail.python.org/pipermail/python-list/2004-May/281943.html

    """
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        # Force the Thread to install our trace.
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed and why == 'line':
            raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True

def simple_decorator(decorator):
    '''This decorator can be used to turn simple functions
    into well-behaved decorators, so long as the decorators
    are fairly simple. If a decorator expects a function and
    returns a function (no descriptors), and if it doesn't
    modify function attributes or docstring, then it is
    eligible to use this. Simply apply @simple_decorator to
    your decorator and it will automatically preserve the
    docstring and function attributes of functions to which
    it is applied.

    Source for function:
    https://wiki.python.org/moin/PythonDecoratorLibrary

    '''
    def new_decorator(f):
        g = decorator(f)
        g.__name__ = f.__name__
        g.__doc__ = f.__doc__
        g.__dict__.update(f.__dict__)
        return g
    # Now a few lines needed to make simple_decorator itself
    # be a well-behaved decorator.
    new_decorator.__name__ = decorator.__name__
    new_decorator.__doc__ = decorator.__doc__
    new_decorator.__dict__.update(decorator.__dict__)
    return new_decorator

def timeout(seconds):
    @simple_decorator
    def decorator(func):
        def wrapped(*args, **kwargs):
            q = Queue.Queue()
            def queue_wrapped(*args, **kwargs):
                q.put(func(*args, **kwargs))
            worker_thread = KThread(target=queue_wrapped, args=args, kwargs=kwargs)
            worker_thread.daemon = True
            worker_thread.start()

            try:
                return q.get(block=True, timeout=seconds)
            except Queue.Empty:
                worker_thread.kill()
                # This should probably be some specific exception or should
                # return None...
                raise
        return wrapped
    return decorator

