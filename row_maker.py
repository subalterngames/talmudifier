from column import Column
from paracol import Paracol
from pdf_reader import PDFReader
from pdf_writer import PDFWriter
from pathlib import Path


class RowMaker:
    """
    Create a target number of rows from a column in a paracol environment.
    """

    def __init__(self, left: bool, center: bool, right: bool, target: str):
        self.paracol = Paracol.get_paracol_header(left, center, right)
        self.switch = Paracol.get_switch_from_left(left, center, right, target)
        self.writer = PDFWriter()

    def get_text_of_length(self, column: Column, target_num_rows: int, expected_length: int) -> (str, Column):
        """
        Returns enough text to fill the target number of rows.

        :param column: The column of words.
        :param target_num_rows: The target number of rows.
        :param expected_length: The expected length of characters. Used as a baseline for row-making.
        """

        col_temp = Column([], column.font, column.font_size)

        # Try to fill the temporary column with the target number of characters.
        filled = False if expected_length > 0 else True
        next_word_index = 0
        while not filled:
            # Get the next word.
            col_temp.words.append(column.words[next_word_index])
            next_word_index += 1

            # Check if we have exceeded the target length.
            row_length_estimate = sum([len(w) for w in col_temp.words])
            filled = row_length_estimate > expected_length

        next_word_index = len(col_temp.words)
        num_rows = 0
        while num_rows != target_num_rows:
            num_rows = self._get_num_rows(col_temp.get_tex(True))

            # Try to overflow the column.
            if num_rows <= target_num_rows:
                # If there no more words to add, return what we've got.
                if next_word_index >= len(column.words):
                    return col_temp.get_tex(True), Column([], column.font, column.font_size)

                # Append a new word.
                col_temp.words.append(column.words[next_word_index])
                next_word_index += 1
            # Walk it back.
            else:
                if len(col_temp.words) == 0:
                    raise Exception("Empty column? I got nothin'.")

                # Remove the last word.
                last_word = col_temp.words[-1]
                col_temp.words.pop()

                num_rows = self._get_num_rows(col_temp.get_tex(True))

                # If removing the last word gave us the target number of rows, try adding hyphenated fragments.
                if num_rows == target_num_rows:
                    for pair in last_word.pairs:
                        # Create a temporary column that includes the first half of the pair.
                        words = col_temp.words[:]
                        words.append(pair[0])
                        col_temp_temp = Column(words, column.font, column.font_size)

                        # The hyphenated fragment fits! Add it and return the truncated column.
                        if self._get_num_rows(col_temp_temp.get_tex(True)) == target_num_rows:
                            words = column.words[len(col_temp.words):]

                            # Insert the second half of the word pair to the words list and add it to a new column.
                            words.insert(0, pair[1])
                            return col_temp_temp.get_tex(True), Column(words, column.font, column.font_size)
                    # No hyphenated pair worked. Return what we've got.
                    return col_temp.get_tex(True), Column(column[len(col_temp.words):], column.font, column.font_size)

    def _get_num_rows(self, tex: str) -> int:
        """
        Returns the number of rows the TeX string fills in the paracol environment.

        :param tex: The TeX string.
        """

        tex = r"\internallinenumbers \begin{linenumbers}" + tex + r"\end{linenumbers} \resetlinenumber[1]"
        tex = self.paracol + tex + "\n\n\\end{paracol}"
        self.writer.write(tex, "line_count")
        output_path = str(Path("Output/line_count.pdf").resolve())
        return PDFReader.get_num_rows(output_path)
