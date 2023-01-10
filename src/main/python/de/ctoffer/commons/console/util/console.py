from commons.util.singleton import Singleton


class Console(metaclass=Singleton):
    def __init__(self):
        self._indent = 0

    def error(self, message: str = "", end: str = '\n'):
        self.print(f"ERROR {message}", end=end)

    def warn(self, message: str = "", end: str = '\n'):
        self.print(f"WARN {message}", end=end)

    def print(self, message: str = "", end='\n'):
        print(self._indent * " " + message, end=end)

    def input(self, message: str) -> str:
        return input(self._indent * " " + message)

    def indent(self):
        self._indent += 2

    def dedent(self):
        self._indent -= 2

    def __enter__(self) -> 'Console':
        self.indent()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dedent()
