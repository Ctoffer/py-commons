from abc import abstractmethod


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


if __name__ == "__main__":
    print(SimpleLineStyle())
    print(SingleBoxDrawingStyle())
    print(DoubleBoxDrawingStyle())
