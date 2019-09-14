from word import Word
from typing import List


class Column:
    def __init__(self, words: List[Word], citation: Citation):
        self._words = List[Word]()
        self.add_words(words)

    def add_word(self, word: Word, index=-1) -> None:
        """
        Add a word to the column.

        :param word: The new word.
        :param index: If this is -1, add the word to the end of the list. Otherwise, add the word at this index.
        """

        if word is None:
            return

        # Add the word at the end of the list.
        if index == -1:
            self._words.append(word)
        # Add the word at the specified index.
        else:
            assert index < len(self._words), f"Invalid word index: {index}. Number of words: {len(self._words)}."
            self._words.insert(index, word)

    def add_words(self, words: List[Word]) -> None:
        """
        Add a list of words to the end of the existing list of words.

        :param words: The new list of words.
        """

        if len(words) == 0:
            return

        # Filter out null words.
        words = [w for w in words if w is not None]

        # Append the new words.
        self._words.extend(words)

    def get_num_words(self) -> int:
        """
        Returns the number of words.
        """

        return len(self._words)

    def get_tex(self, close_braces: bool, start_index=0, end_index=-1) -> str:
        """
        Generate a LaTeX string from the words.

        :param close_braces: If true, make sure that all curly braces are closed.
        :param start_index: The start index.
        :param end_index: The end index. If this is -1, it is ignored.
        """

        tex = ""

        states = [False, False, False, False, False]

        if end_index == -1:
            end_index = len(self._words)

        for i in range(start_index, end_index):
            word = self._words[i]
            for (style, j, word_style, tex_cmd) in zip(states[:], range(len(states)),
                                                       [word.bold, word.italic, word.underline, word.smallcaps, word.citation],
                                                       [r"\textbf{", r"\textit{", r"\underline{", r"\textsc{", r"\red{"]):
                if word_style and not style:
                    states[j] = True
                    tex += tex_cmd
                elif not word_style and style:
                    states[j] = False
                    tex += "}"
                # Add the margin note, if any.
                tex += word + word.get_margin_note() + " "

        # Close the braces in the column.
        if close_braces:
            num_braces = 0
            for c in tex:
                if c == "{":
                    num_braces += 1
                elif c == "}":
                    num_braces -= 1
            for i in range(num_braces):
                tex += "}"
            return tex
        # Return the string as-is.
        else:
            return tex
