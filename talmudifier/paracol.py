from box import Box
from pdf_reader import PDFReader
from pdf_writer import PDFWriter


class Paracol:
    """
    A LaTeX paracol environment, composed of boxes.
    """

    TWO_THIRDS = str(2.0 / 3)
    ONE_THIRD = str(1.0 / 3)
    END = "\n\n\\end{paracol}"

    def __init__(self, left: Box,
                 center: Box,
                 right: Box,
                 font_left: str,
                 font_center: str,
                 font_right: str):
        """
        :param left: The left box.
        :param center: The center box.
        :param right: The right box.
        :param font_left: The left font command.
        :param font_center: The center font command.
        :param font_right: The right font command.
        """

        self.left = left
        self.center = center
        self.right = right
        self.font_left = font_left
        self.font_center = font_center
        self.font_right = font_right

        # Set the environment header.
        if len(self.left.words) > 0 and len(self.center.words) > 0 and len(self.right.words) > 0:
            self.header = r"\begin{paracol}{3}"
        elif len(self.left.words) > 0 and len(self.right.words) > 0:
            self.header = r"\begin{paracol}{2}"
        elif len(self.left.words) > 0 and len(self.center.words) > 0:
            self.header = r"\columnratio{" + Paracol.ONE_THIRD + "}\n" + r"\begin{paracol}{2}"
        elif len(self.center.words) > 0 and len(self.right.words) > 0:
            self.header = r"\columnratio{" + Paracol.TWO_THIRDS + "}\n" + r"\begin{paracol}{2}"
        else:
            self.header = ""
