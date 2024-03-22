

from math import floor, log10
# get magnitude of number
def magnitude(n: int) -> int:
    return int(floor(log10(abs(n))))

def first_two_digits(n: int) -> int:
    digits = str(n)[:2]
    return int(digits) / 10

def get_steps(n: int) -> str:
    return f'{first_two_digits(n)}e{magnitude(n)}'

print(magnitude(100))
print(first_two_digits(1400))
print(get_steps(1400))
