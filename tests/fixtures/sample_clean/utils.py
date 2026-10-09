"""Helper utilities used by the calculator module.

Demo purpose: proper `with` usage and specific exception handling only.
"""


def format_result(value, precision=2):
    return round(value, precision)


def validate_number(value):
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid number: {value}") from exc


def log_operation(operation, result):
    with open("operations.log", "a") as f:
        f.write(f"{operation} = {result}\n")
