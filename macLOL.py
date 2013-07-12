import numpy as np

def euclid_extended(a, b):
    """Computes (x, y), the values that satisfy a * x + b * y = gcd(a, b).

    See http://en.wikipedia.org/wiki/Extended_Euclidean_algorithm

    >>> euclid_extended(120, 23)
    (-9, 47)

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

    """
    product = np.product(moduli)
    summation = 0

    for i in range(len(moduli)):
        x, y = euclid_extended(moduli[i], product / moduli[i])
        summation += residues[i] * y * (product / moduli[i])
    return summation % product

if __name__ == '__main__':
    print euclid_extended(3, 20)
    print chinese_remainder_theorem([2, 3, 1], [3, 4, 5])

