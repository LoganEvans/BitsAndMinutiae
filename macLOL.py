import numpy as np
import random

MAX_WIDTH = 30

def euclid_extended(a, b):
    """Computes (x, y), the values that satisfy a * x + b * y = gcd(a, b).

    See http://en.wikipedia.org/wiki/Extended_Euclidean_algorithm

    >>> euclid_extended(120, 23)
    (-9, 47)
    >>> euclid_extended(3, 20)
    (7, -1)

    """
    x = 0
    lastx = 1
    y = 1
    lasty = 0
    while b:
        quotient = a / b
        a, b = b, a % b
        x, lastx = lastx - quotient * x, x
        y, lasty = lasty - quotient * y, y
    return lastx, lasty

def chinese_remainder_theorem(residues, moduli):
    """
    See http://en.wikipedia.org/wiki/Chinese_remainder_theorem

    >>> chinese_remainder_theorem([2, 3, 1], [3, 4, 5])
    11

    """
    product = np.product(moduli)
    summation = 0

    for i in xrange(len(residues)):
        x, y = euclid_extended(moduli[i], product / moduli[i])
        summation += residues[i] * y * (product / moduli[i])
    return summation % product

def pprime(n):
    """
    Miller-Rabin primality test.

    A return value of False means n is certainly not prime. A return value of
    True means n is very likely a prime.

    >>> pprime(1234567891)
    True

    """

    if not (n >= 2):
        return False
    # special case 2
    if n == 2:
       return True
    # ensure n is odd
    if n % 2 == 0:
       return False
    s = 0
    d = n-1
    while True:
       quotient, remainder = divmod(d, 2)
       if remainder == 1:
           break
       s += 1
       d = quotient

    # test the base a to see whether it is a witness for the compositeness of n
    def try_composite(a):
        if pow(a, d, n) == 1:
            return False
        for i in xrange(s):
            if pow(a, (2 ** i) * d, n) == n - 1:
                return False
        return True # n is definitely composite

    # The magic number should be something greater than 3. The larger it is, the
    # lower the chance of a false positive.
    for i in xrange(5):
        a = random.randrange(2, n)
        if try_composite(a):
            return False

    return True # no base tested showed n as composite

def gen_primes():
    yield 2
    val = 3
    while True:
        if pprime(val):
            yield val
        val += 2

def create_moduli(max_val):
    """
    >>> create_moduli(4)
    [4, 9, 5, 7]
    >>> create_moduli(6)
    [8, 9, 25, 7, 11, 13]

    """
    moduli = []
    prime_generator = gen_primes()
    for _ in xrange(max_val):
        base_modulus = next(prime_generator)
        new_modulus = base_modulus
        while new_modulus < max_val:
            new_modulus *= base_modulus
        moduli.append(new_modulus)
    return moduli

class MemPool(object):
    """
    >>> M = MemPool(10)
    >>> a = M.macLOL(2)
    >>> a[0], a[1] = 'a', 'a'
    >>> b = M.macLOL(3)
    >>> b[0], b[1], b[2] = 'b', 'b', 'b'
    >>> c = M.macLOL(4)
    >>> c[0], c[1], c[2], c[3] = 'c', 'c', 'c', 'c'
    >>> d = M.macLOL(1)
    >>> d[0] = 'd'
    >>> print M
    finger: 3564097275952
     0: a  1: a  2: b  3: b  4: b  5: c  6: c  7: c  8: c  9: d 
    >>> b.freeLOL()
    >>> d.freeLOL()
    >>> print M
    finger: 3564097275952
     0: a  1: a |2: b||3: b||4: b| 5: c  6: c  7: c  8: c |9: d|
    >>> e = M.macLOL(4)
    >>> e[0], e[1], e[2], e[3] = 'e', 'e', 'e', 'e'
    >>> print M
    finger: 3564097275952
     0: a  1: a  2: e  3: e  4: e  5: c  6: c  7: c  8: c  9: e 
    >>> ea = e.macLOL(2)
    >>> ea[0], ea[1] = 'EA', 'EA'
    >>> eb = e.macLOL(2)
    >>> eb[0], eb[1] = 'EB', 'EB'
    >>> print M
    finger: 3564097275952
     0:  a  1:  a  2: EA  3: EA  4: EB  5:  c  6:  c  7:  c  8:  c  9: EB 
    >>> print e
    finger: 5710520941554
     0: EA  1: EA  2: EB  3: EB 

    """
    def __init__(self, size, arena=None, finger=None):
        self.size = size
        self.used = [False for _ in xrange(self.size)]
        self.num_used = 0
        if arena:
            self.arena = arena
        else:
            self.arena = [None for _ in xrange(self.size)]

        if arena and isinstance(arena, MemPool):
            self.moduli = self.arena.moduli
        else:
            self.moduli = create_moduli(self.size)

        if finger:
            self.finger = finger
        else:
            self.finger = chinese_remainder_theorem(list(xrange(self.size)),
                                                    self.moduli)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.arena[self.finger % self.moduli[key]]
        elif isinstance(key, slice):
            return [self.arena[self.finger % self.moduli[val]]
                    for val in xrange(*key.indices(self.size))]
        else:
            raise TypeError("Invalid argument type.")

    def __setitem__(self, key, item):
        if isinstance(key, int):
            self.arena[self.finger % self.moduli[key]] = item
        elif isinstance(key, slice):
            for index in xrange(key.start, key.stop, key.step):
                self.arena[self.finger % self.moduli[index]] = item
        else:
            raise TypeError("Invalid argument type.")

    def __len__(self):
        return self.size

    def __iter__(self):
        return self

    def next(self):
        try:
            self._iter_index += 1
        except AttributeError:
            self._iter_index = 0

        if self._iter_index >= self.size:
            self._iter_index = 0
            raise StopIteration()
        else:
            return self[self._iter_index]

    def __str__(self):
        width = 0
        for val in self:
            try:
                width = max(width, len(str(val)))
            except TypeError:
                pass
        width += 1
        tmpl = "{used}{index:2>}:{value:>" + str(width) + "}{used}"

        # finger
        builder = ["finger: {finger}\n".format(finger=self.finger)]
        for i in xrange(self.size):
            builder += [tmpl.format(used=" " if self.used[i] else "|",
                                    value=str(self[i]),
                                    index=i)]

        return ''.join(builder)

    def macLOL(self, size):
        if size > self.size - self.num_used:
            raise MemoryError(
                    "{0} blocks requested but only {1} available.".format(
                            size, self.size - self.num_used))
        else:
            self.num_used += size

        residues = []
        index = 0
        while len(residues) < size:
            if not self.used[index]:
                residues.append(index)
                self.used[index] = True
            index += 1

        return MemPool(size, arena=self,
                       finger=chinese_remainder_theorem(residues, self.moduli))

    def freeLOL(self):
        if not isinstance(self.arena, MemPool):
            # The arena is a list(), so let the GC take care of it.
            pass
        else:
            for i in xrange(self.size):
                self.arena.used[self.finger % self.moduli[i]] = False
            self.arena.num_used -= self.size

