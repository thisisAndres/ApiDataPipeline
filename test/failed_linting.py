"""Sample python file, which is properly linted."""


class Test:
    """Sample class."""
    def __init__(self):
        self.a = 5

    def print_a(self):
        print(self.a)


if __name__ == "__main__":
    t = Test()
    t.print_a()