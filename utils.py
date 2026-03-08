def log_print(message, log_file):
    """Print to console and log file simultaneously."""
    print(message)
    log_file.write(message + "\n")
    log_file.flush()


def get_fizzbuzz_response(number: int, fizz_num: int = 3, buzz_num: int = 5) -> str:
    """
    Returns the correct Fizzbuzz response for a given number.

    Args:
        number: The current turn number
        fizz_num: The number to check for "fizz" (default: 3)
        buzz_num: The number to check for "buzz" (default: 5)

    Rules:
    - Divisible by both fizz_num and buzz_num: "fizzbuzz"
    - Divisible by fizz_num: "fizz"
    - Divisible by buzz_num: "buzz"
    - Otherwise: the number itself as a string
    """
    if number % fizz_num == 0 and number % buzz_num == 0:
        return "fizzbuzz"
    elif number % fizz_num == 0:
        return "fizz"
    elif number % buzz_num == 0:
        return "buzz"
    else:
        return str(number)
