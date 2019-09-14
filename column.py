from word import Word
from typing import List, Optional
from style import Style


class Column:
    """
    A column is a list of words and a font rule.
    From this, a valid block of TeX text can be generated.
    """

    def __init__(self, words: List[Word], font: str, font_size: str):
        """
        :param words: The list of words in the column.
        :param citation: The citation object used to generate citations.
        :param font: The command used to start the font.
        :param font_size: The font size command.
        """

        self.words = words
        self.font = font
        self.font_size = font_size

    def get_tex(self, close_braces: bool, extra_word: Optional[Word], start_index=0, end_index=-1) -> str:
        """
        Generate a LaTeX string from the words.

        :param close_braces: If true, make sure that all curly braces are closed.
        :param extra_word: An optional extra word, e.g. a hyphenated fragment.
        :param start_index: The start index.
        :param end_index: The end index. If this is -1, it is ignored.
        """

        # Add an extra word, e.g. a hyphenated fragment.
        words = self.words[:]
        if extra_word is not None:
            words.append(extra_word)

        # Start the text with the font size and the font command.
        tex = self.font_size + self.font + " "

        style = Style(False, False, False)

        # Get the slice of words.
        if end_index == -1:
            end_index = len(words)

        for word in words[start_index: end_index]:
            # Add a citation word.
            if word.is_citation:
                # Close all braces.
                tex = Column._close_braces(tex)
                tex += " " + word.word + " " + self.font + " "
                continue

            # Set bold style.
            if word.style.bold and not style.bold:
                tex += r"\textbf{"
                style.bold = True
            elif not word.style.bold and style.bold:
                tex += "}"
                style.bold = False
            # Set italic style.
            if word.style.italic and not style.italic:
                tex += r"\textit{"
                style.italic = True
            elif not word.style.italic and style.italic:
                tex += "}"
                style.italic = False
            # Set underline style.
            if word.style.underline and not style.underline:
                tex += r"\underline{"
                style.underline = True
            elif not word.style.underline and style.underline:
                tex += "}"
                style.underline = False

            # Append the word.
            tex += word.word + " "

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
