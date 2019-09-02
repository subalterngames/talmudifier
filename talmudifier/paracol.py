from box import Box
from pdf_reader import PDFReader
from pdf_writer import PDFWriter


class Paracol:
    """
    A LaTeX paracol environment, composed of boxes.
    """

    # TODO font!

    TWO_THIRDS = str(2.0 / 3)
    ONE_THIRD = str(1.0 / 3)
    END = "\n\n\\end{paracol}"

    def __init__(self, left: Box,
                 center: Box,
                 right: Box,
                 font_left: str,
                 font_center: str,
                 font_right: str,
                 phantom=""):
        """
        :param left: The left box.
        :param center: The center box.
        :param right: The right box.
        :param font_left: The left font command.
        :param font_center: The center font command.
        :param font_right: The right font command.
        :param phantom: The name of an empty column. Can be "left", "center", "right", or "".
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
        self.phantom = phantom

    def _get_column(self, column: str) -> Box:
        """
        Returns the left, center, or right column.

        :param column: The name of the column. May be "left", "center", or "right".
        """
        if column == "left":
            return self.left
        elif column == "center":
            return self.center
        elif column == "right":
            return self.right
        else:
            raise Exception(f"No column named: {column}")

    def _get_switch_to_from_left(self, column: str) -> str:
        """
        Returns the switch command required to switch to this column from the left column.

        :param column: The name of the column.
        """

        if column == "left":
            return ""
        elif column == "center":
            if len(self.left.words) > 0:
                return r"\switchcolumn"
            else:
                return ""
        elif column == "right":
            if len(self.left.words) > 0:
                if len(self.center.words) > 0:
                    return r"\switchcolumn[2]"
                else:
                    return r"\switchcolumn"
            elif len(self.center.words) > 0:
                return r"\switchcolumn"
            else:
                return ""
        else:
            raise Exception(f"No column named: {column}")

    def get_num_rows(self, column: str, start_index=0, end_index=-1) -> int:
        """
        Returns the number of rows a given column will be in this paracol environment.

        :param column: The name of the column.
        :param start_index: The start index of the words.
        :param end_index: The end index of the words. If this is -1, it is the end of the list.
        """

        col = self._get_column(column)
        switch = self._get_switch_to_from_left(column)

        # Get the LaTeX string.
        tex = self.header + switch + "\n" + col.get_tex(True, start_index=start_index, end_index=end_index)

        PDFWriter().write(tex, "temp")
        return PDFReader.get_num_rows("temp")

