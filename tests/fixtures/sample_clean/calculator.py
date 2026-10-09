"""Simple calculator module - clean reference implementation.

Demo purpose: no anti-patterns present. Expected CRS: ~95-100.
"""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)


def main():
    print(add(2, 3))
    print(subtract(5, 2))
    print(multiply(4, 3))
    print(divide(10, 2))
    print(calculate_average([1, 2, 3, 4, 5]))


if __name__ == "__main__":
    main()
