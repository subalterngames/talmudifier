from word import Word
from typing import List
from style import Style


class Column:
    """
    A column is a list of words and a font rule.
    From this, a valid block of TeX text can be generated.
    """

    def __init__(self, words: List[Word], font: str, font_size: int, font_skip: int):
        """
        :param words: The list of words in the column.
        :param font: The command used to start the font.
        :param font_size: The font size.
        :param font_skip: The font skip size.
        """

        self.words = words
        self.font = font
        self.font_size = font_size
        self.font_skip = font_skip

        if self.font_size > 0 and self.font_skip > 0:
            self.font_command = "\\fontsize{" + str(font_size) + "}{" + str(font_skip) + "}"
        else:
            self.font_command = ""

    def get_tex(self, close_braces: bool, start_index=0, end_index=-1) -> str:
        """
        Generate a LaTeX string from the words.

        :param close_braces: If true, make sure that all curly braces are closed.
        :param start_index: The start index.
        :param end_index: The end index. If this is -1, it is ignored.
        """

        # Start the text with the font size and the font command.
        tex = self.font_command + self.font + " "

        style = Style(False, False, False)

        # Get the slice of words.
        if end_index == -1:
            end_index = len(self.words)

        for word, w in zip(self.words[start_index: end_index], range(start_index, end_index)):
            # Add a citation word.
            if word.is_citation:
                # Close all braces.
                tex = Column._close_braces(tex)
                tex += word.word + " " + self.font + " "
                continue

            # Set bold style.
            if word.style.bold and not style.bold:
                tex += r"\textbf{"
                style.bold = True
            # Set italic style.
            if word.style.italic and not style.italic:
                tex += r"\textit{"
                style.italic = True
            # Set underline style.
            if word.style.underline and not style.underline:
                tex += r"\underline{"
                style.underline = True

            # Append the word.
            tex += word.word

            # Try to close style braces.
            if w < end_index - 1:
                next_word = self.words[w + 1]
                if style.bold and not next_word.style.bold:
                    style.bold = False
                    tex += "}"
                if style.italic and not next_word.style.italic:
                    style.italic = False
                    tex += "}"
                if style.underline and not next_word.style.underline:
                    style.underline = False
                    tex += "}"

                tex += " "

        if close_braces:
            tex = Column._close_braces(tex)

        return tex

    @staticmethod
    def _close_braces(tex: str) -> str:
        """
        Add a } for every {.

        :param tex: The TeX string.
        """

        num_braces = 0
        for c in tex:
            if c == "{":
                num_braces += 1
            elif c == "}":
                num_braces -= 1
        for i in range(num_braces):
            tex += "}"
        return tex
