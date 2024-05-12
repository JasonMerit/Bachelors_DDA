import time
from math import floor, log10
START = time.time()
def _start():
    global _START
    START = time.time()

AVG = 0
def end():
    # global AVG
    t = time.time() - START
    # AVG += .1 * (t - AVG)
    # print(f'{AVG:.2f}, {t:.2f}')
    print(f'{t = :.2f}')
    _start()

def magnitude(n: int) -> int:
    return int(floor(log10(abs(n))))

def first_two_digits(n: int) -> float:
    digits = str(n)[:2]
    return int(digits) / 10

def get_steps(n: int) -> str:
    return f'{first_two_digits(n)}e{magnitude(n)}'