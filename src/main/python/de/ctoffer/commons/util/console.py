from abc import abstractmethod, ABC

from commons.creational.singleton import singleton


class LineStyle:
    @property
    def v(self):
        return self.get_vertical_line()

    @property
    def h(self):
        return self.get_horizontal_line()

    @property
    def tl(self):
        return self.get_top_left_corner()

    @property
    def tr(self):
        return self.get_top_right_corner()

    @property
    def bl(self):
        return self.get_bottom_left_corner()

    @property
    def br(self):
        return self.get_bottom_right_corner()

    @property
    def c(self):
        return self.get_cross()

    @property
    def lc(self):
        return self.get_left_to_center()

    @property
    def rc(self):
        return self.get_right_to_center()

    @property
    def tc(self):
        return self.get_top_to_center()

    @property
    def bc(self):
        return self.get_bottom_to_center()

    @abstractmethod
    def get_vertical_line(self):
        raise NotImplementedError

    @abstractmethod
    def get_horizontal_line(self):
        raise NotImplementedError

    @abstractmethod
    def get_top_left_corner(self):
        raise NotImplementedError

    @abstractmethod
    def get_top_right_corner(self):
        raise NotImplementedError

    @abstractmethod
    def get_bottom_left_corner(self):
        raise NotImplementedError

    @abstractmethod
    def get_bottom_right_corner(self):
        raise NotImplementedError

    @abstractmethod
    def get_cross(self):
        raise NotImplementedError

    @abstractmethod
    def get_left_to_center(self):
        raise NotImplementedError

    @abstractmethod
    def get_right_to_center(self):
        raise NotImplementedError

    @abstractmethod
    def get_top_to_center(self):
        raise NotImplementedError

    @abstractmethod
    def get_bottom_to_center(self):
        raise NotImplementedError

    def __str__(self):
        h = 4 * self.h
        s = 4 * " "

        line1 = self.tl + h + self.tc + h + self.tr
        line2 = self.v + s + self.v + s + self.v
        line3 = self.lc + h + self.c + h + self.rc
        line4 = self.v + s + self.v + s + self.v
        line5 = self.bl + h + self.bc + h + self.br

        return "\n".join((line1, line2, line3, line4, line5))


class SimpleLineStyle(LineStyle):
    def get_vertical_line(self):
        return "|"

    def get_horizontal_line(self):
        return "-"

    def get_top_left_corner(self):
        return self.get_cross()

    def get_top_right_corner(self):
        return self.get_cross()

    def get_bottom_left_corner(self):
        return self.get_cross()

    def get_bottom_right_corner(self):
        return self.get_cross()

    def get_cross(self):
        return "+"

    def get_left_to_center(self):
        return self.get_cross()

    def get_right_to_center(self):
        return self.get_cross()

    def get_top_to_center(self):
        return self.get_cross()

    def get_bottom_to_center(self):
        return self.get_cross()


class SingleBoxDrawingStyle(LineStyle):
    def get_vertical_line(self):
        return "│"

    def get_horizontal_line(self):
        return "─"

    def get_top_left_corner(self):
        return "┌"

    def get_top_right_corner(self):
        return "┐"

    def get_bottom_left_corner(self):
        return "└"

    def get_bottom_right_corner(self):
        return "┘"

    def get_cross(self):
        return "┼"

    def get_left_to_center(self):
        return "├"

    def get_right_to_center(self):
        return "┤"

    def get_top_to_center(self):
        return "┬"

    def get_bottom_to_center(self):
        return "┴"


class DoubleBoxDrawingStyle(LineStyle):
    def get_vertical_line(self):
        return "║"

    def get_horizontal_line(self):
        return "═"

    def get_top_left_corner(self):
        return "╔"

    def get_top_right_corner(self):
        return "╗"

    def get_bottom_left_corner(self):
        return "╚"

    def get_bottom_right_corner(self):
        return "╝"

    def get_cross(self):
        return "╬"

    def get_left_to_center(self):
        return "╠"

    def get_right_to_center(self):
        return "╣"

    def get_top_to_center(self):
        return "╦"

    def get_bottom_to_center(self):
        return "╩"


@singleton
class ConsoleIO:
    def __init__(self):
        self._level = 0

    @property
    def padding(self):
        return 2 * self._level * ' '

    def __enter__(self):
        self._level += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._level -= 1

    def debug(self, message: str) -> None:
        print(f"# {self.padding}{message}")

    def info(self, message: str) -> None:
        print(f"{self.padding}{message}")

    def error(self, message: str) -> None:
        print(f"E {self.padding}{message}")

    def ask(self, question: str) -> str:
        return input(f"{self.padding}>: {question}")


def resolve_padding(padding) -> tuple:
    if isinstance(padding, int):
        result = (padding, padding, padding, padding)
    elif isinstance(padding, tuple):
        if len(padding) == 2:
            top, left = padding
            result = (top, top, left, left)
        elif len(padding) == 4:
            result = padding
        else:
            raise ValueError("Expected tuple (top, left) or tuple (top, bot, left, right)")
    else:
        raise ValueError("Expected padding: int or (top, left) or (top, bot, left, right)")

    return result


def block_align(lines, width, alignment) -> tuple:
    print("block_align", width)
    result = list()
    buffer = ""
    lines = [(i, line.split(" ")) for i, line in enumerate(lines)]

    for i, words in lines:
        for word in words:
            if sum(map(len, buffer)) + 1 + len(word) > width and buffer:
                result.append(buffer)
                buffer = ""

            if buffer:
                buffer += " "
            buffer += word

        if buffer:
            result.append(buffer)
            buffer = ""

        if i < len(lines) - 1:
            result.append(" " * width)

    print("w", width)
    width = max(width, *(map(len, result)))
    line_format = f"{{:{alignment + str(width) + 's'}}}"

    return tuple(map(line_format.format, result))


class Renderable(ABC):
    def __init__(self, content: list):
        self._content = content

    @abstractmethod
    def render(self, rendering):
        for line in self._content:
            rendering(line)


class Boxed(Renderable):
    def __init__(self, lines: list, width: 80, style=SingleBoxDrawingStyle, alignment='^', padding=0):
        self._style = style()
        self._padding = resolve_padding(padding)
        width = Boxed._normalize_width(width, self._padding, lines)
        print(width, "vs", len(lines[0]) + padding[2] + padding[3])

        segment = (len(lines[0]) + padding[2] + padding[3]) * self._style.h
        padding_line = self._style.v + (len(lines[0]) + padding[2] + padding[3]) * ' ' + self._style.v
        line_format = f"{{v}}{' ' * self._padding[2]}{{line}}{' ' * self._padding[3]}{{v}}"

        self._lines = [self._style.tl + segment + self._style.tr]
        for _ in range(self._padding[0]):
            self._lines.append(padding_line)
        print(lines[0], len(lines[0]))
        self._lines.extend(map(lambda line: line_format.format(v=self._style.v, line=line), lines))
        for _ in range(self._padding[1]):
            self._lines.append(padding_line)
        self._lines.append(self._style.bl + segment + self._style.br)

        super().__init__(self._lines)

    @staticmethod
    def _normalize_width(width, padding, lines):
        lines = [(i, line.split(" ")) for i, line in enumerate(lines)]
        biggest_word_len = max(len(word) for i, words in lines for word in words)

        return max(width, biggest_word_len+2)

    def render(self, rendering):
        for line in self._lines:
            rendering(line)


class BoxedText(Boxed):
    def __init__(self, message: str, width: 80, style=SingleBoxDrawingStyle, alignment='^', padding=0):
        padding = resolve_padding(padding)
        aligned_lines = block_align(
            message.split("\n"),
            width - padding[2] - padding[3],
            alignment
        )

        super().__init__(
            lines=aligned_lines,
            width=width,
            style=style,
            alignment=alignment,
            padding=padding
        )


class Table:
    def __init__(self, table_data, width: 80):
        pass


if __name__ == "__main__":
    print(SimpleLineStyle())
    print(SingleBoxDrawingStyle())
    print(DoubleBoxDrawingStyle())

    text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod_ tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. " \
           "At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. " \
           "\n" \
           "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. " \
           "At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet."
    text = "Hello World"
    ConsoleIO.instance.info("Hello World")
    for i in range(4, 12):
        box = BoxedText(text + " " + str(i), width=i, padding=(1, 1))
        box.render(ConsoleIO.instance.info)
