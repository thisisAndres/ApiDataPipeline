"""Sample python file, which is properly linted."""


class Test:
    """Sample class."""

    def __init__(self):
        """Constructor."""
        self.a = 5

    def print_a(self):
        """Print variable a."""
        print(self.a)  # noqa


if __name__ == "__main__":
    t = Test()
    t.print_a()
