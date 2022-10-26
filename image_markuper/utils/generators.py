import random
import string


def generate_charset(length: int) -> str:
    """Generate a random string of characters of a given length."""
    return "".join(random.choice(string.ascii_letters) for _ in range(length))
