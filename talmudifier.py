from pathlib import Path
import re
from typing import List
from sys import platform
from os import devnull
from os.path import join, exists
import math
import io


class Word:
    """
    Strip a markdown word to the actual text and save the styling metadata.

    :param markdown_word: The markdown word, e.g. _**this!**_
    """

    H = Hyphenator('en_US')
    SYMBOLS = {"|": r"$\mid$",
               "א": r"\<'>",
               "ב": r"\<b>",
               "׃": r"\<;>",
               "●": r"\CIRCLE",
               "◐": r"\LEFTcircle"
               }

    def __init__(self, word: str, bold: bool, italic: bool, underline: bool, smallcaps: bool, citation: bool,
                 margin_note=None):
        """
        :param word: The actual word, stripped of any markdown styling.
        :param bold: If true, this word is bolded.
        :param italic: If true, this word is italicized.
        :param underline: If true, this word is underlined.
        :param smallcaps: If true, this word is in smallcaps.
        :param citation: If true, this word is a citation.
        :param margin_note: The margin note, if any.
        """

        self.word = word
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.smallcaps = smallcaps
        self.citation = citation
        self.margin_note = margin_note

    def get_hyphenated_pairs(self) -> list:
        """
        Get all possible hyphenated pairs of this word (e.g. Cal- ifornia).
        """

        pairs_text = self.H.pairs(self.word)
        pairs = []

        for pair in pairs_text:
            # Append the hyphen to the first word.
            p0 = pair[0] + "-"
            p1 = pair[1]
            h = []

            # Add pairs of Word objects.
            for p in [p0, p1]:
                # Add the margin note only to the first fragment.
                margin_note = self.margin_note if p == p0 else None
                w = Word(p, self.bold, self.italic, self.underline, self.smallcaps, self.citation, margin_note)

                h.append(w)
            pairs.append(h)
        return pairs


class TextBlock:
    """
    A block of text, containing many words.
    """

    def __init__(self, words: List[Word]):
        """
        :param words: The words in the block.
        """

        self._words = words
        self.tex = self._get_tex()

    def add_word(self, word: Word):
        """
        Add a word. Regenerate the tex string.

        :param word: The new word.
        """

        # TODO index
        # TODO add at end

        self._words.append(word)
        self.tex = self._get_tex()

    def _get_tex(self) -> str:
        """
        Generates LaTeX text from the words.
        """

        tex = ""

        # Create a style state.
        bold = False
        italic = False
        underline = False
        smallcaps = False
        citation = False

        states = [bold, italic, underline, smallcaps, citation]

        # Iterate through each word.
        for word in self._words:
            # Iterate through the global style state, the word style state, and the tex commands.
            for (style, i, word_style, tex_cmd) in zip(states[:], range(len(states)),
                                                    [word.bold, word.italic, word.underline, word.smallcaps, word.citation],
                                                    [r"\textbf{", r"\textit{", r"\underline{", r"\textsc{", r"\red{"]):
                if word_style and not style:
                    states[i] = True
                    tex += tex_cmd
                elif not word_style and style:
                    states[i] = False
                    tex += "}"
            # Append the text.
            if tex != "":
                tex += " "
            tex += word.word

        return tex

class Column:
    """
    A column filled with words.
    """

    def __init__(self, txt: str, smallcap_words: List[str]):
        """
        :param txt: The column's raw markdown text.
        :param smallcap_words: The words reserved for smallcaps.
        """

        # Get all of the words in this column.
        self.words = [Word(w, w in smallcap_words) for w in txt.split(" ")]


class TexState:
    """
    The current state of LaTeX stylings.
    """

    def __init__(self):
        self.bold = False
        self.italic = False
        self.underline = False
        self.smallcaps = False
        self.citation = False

        self.states = [self.bold, self.italic, self.underline, self.smallcaps, self.citation]


class Row:
    """
    A row in a table.
    """

    def __init__(self, state: TexState, text=""):
        self.text = text

        if self.text == "":
            if state.bold:
                self.text += r"\textbf{"
            if state.italic:
                self.text += r"\textit{"
            if state.underline:
                self.text += r"\underline{"

    @staticmethod
    def close_off_row(row: str) -> str:
        """
        Add enough } to create valid LaTeX.

        :param row: The row.
        """

        # Close off all braces.
        num_braces = 0
        for c in row:
            if c == "{":
                num_braces += 1
            elif c == "}":
                num_braces -= 1
        for i in range(num_braces):
            row += "}"
        return row

    def finish_tex(self) -> None:
        """
        Close off the row's curly braces and create a box.
        """

        self.text = r"\makebox[\linewidth][s]{" + Row.close_off_row(self.text).strip() + "}"


class Talmudifier:
    def __init__(self, text_left: str, text_center: str, text_right: str,
                 text_title=None,
                 font_left_package=r"\usepackage{CormorantGaramond}",
                 font_center_command=r"\DeclareRobustCommand{\palatino}{\fontfamily{ppl}\selectfont}",
                 font_right_command=r"\DeclareRobustCommand{\bskfamily}{\fontencoding{OT1}\fontfamily{bsk}\selectfont}",
                 font_center=r"\palatino{\large",
                 font_right=r"\bskfamily{",
                 preamble_filename="header.txt",
                 smallcap_words=["Asherah"],
                 bold_font=r"\bskfamily{\textbf{"):
        """
        :param text_left: The text in the left column. May be None.
        :param text_center: The text in the center column. May be None.
        :param text_right: The text in the right column. May be None.
        :param text_title: The title of the page. May be None.
        :param font_left_package: The package used for the left column's font (i.e. the default font). Default = Cormorant Garamond.
        :param font_center_command: The command definition for the font used in the center column. Default = Palatino.
        :param font_right_command: The command definition for the font used in the right column. Default = Boisik.
        :param font_center: The command for the font used in the center column.
        :param font_right: The command for the font used in the right column.
        :param preamble_filename: The filename of the preamble.
        :param smallcap_words: Words that will always be in smallcaps.
        :param bold_font: The font used for bold words. May be None.
        """

        # Get the preamble text.
        preamble_path = Path(preamble_filename)
        assert preamble_path.exists(), f"Preamble file not found: {preamble_path}"
        self.preamble = Path(preamble_filename).read_text()

        # Append the font declarations.
        self.preamble += f"\n{font_left_package}\n{font_center_command}\n{font_right_command}\n\n"
        # Begin the document.
        self.preamble += r"\begin{document}\begin{sloppypar}" + "\n\n"
        self.doc = self.preamble[:]

        # Generate the title.
        if text_title:
            self.doc += r"\chapter{" + text_title + "}\n\n"

        self.bold_font = bold_font

        # Generate the columns.
        self.columns = [Column(t, smallcap_words=smallcap_words)
                        for t in [text_left, text_center, text_right]]

        # Set and create the output directory.
        self.output_directory = Path("../Output")
        if not self.output_directory.exists():
            self.output_directory.mkdir()
        self.output_directory = str(self.output_directory.resolve())

        self.font_center = font_center
        self.font_right = font_right

        self.state = TexState()

    def create(self) -> None:
        """
        Create the PDF page.
        """

        self.columns, four_rows = self.get_four_rows_left_right(self.columns)
        self.doc += four_rows

        self.columns, row = self.get_one_row_left_right(self.columns)
        self.doc += row
        self.doc += row

        done = False
        while not done:
            # Generate a table.
            done, tex = self.generate_paracol_table()
            self.doc += tex[:]
            if not done:
                self.doc += tex[:]
                # Generate an extra row.
                done, tex = self.generate_one_more_row()
                self.doc += tex

        # Finish the doc.
        self.doc += r"\end{sloppypar}\end{document}"
        print(self.doc)

    def get_row(self, table: Table, column_name: str, switch_column: str, paracol=None) -> (Table, Row):
        """
        Build a new row from a column of words.

        :param table: The current table.
        :param column_name: The name of the column.
        :param switch_column: The switch column command
        :param paracol: The paracol header.
        """

        col = table.columns[column_name]

        if len(col.words) == 0:
            return table, ""

        # Get the paracol header.
        if paracol is None:
            paracol = table.get_paracol_header()

        # Switch to the correct column.
        if column_name != "left":
            paracol += f"\n\t{switch_column}\n"

        row = Row(self.state)

        # Set the correct font.
        if column_name == "center":
            row.text = self.font_center
        elif column_name == "right":
            row.text = self.font_right

        done = False
        while not done:
            row, col, done = self._get_next_word_in_row(row, col, paracol)
            # Set the column.
            table.columns[column_name] = col
        return table, row

    def get_four_rows_left_right(self, columns: List[Column]) -> (List[Column], str):
        """
        Generate a table with two columns, four rows each.
        :param columns: The columns of words.
        """

        table = Table(columns[0],
                      columns[1],
                      columns[2],
                      False)
        paracol = r"\begin{paracol}{2}" + "\n"
        paracol_original = paracol[:]

        # Get four rows on the left and right.
        for column_name in ["left", "right"]:
            rows = ""
            for i in range(4):
                table, row = self.get_row(table, column_name, r"\switchcolumn", paracol=paracol_original)
                rows += row.text
                if i < 3:
                    rows += r"\newline"
            paracol += rows
            if column_name == "left":
                paracol += "\n\n\\switchcolumn\n\n"
        paracol += "\n\n\\end{paracol}"

        # Update the columns.
        columns[0] = table.columns["left"]
        columns[1] = table.columns["center"]
        columns[2] = table.columns["right"]
        return columns, paracol

    def get_one_row_left_right(self, columns: List[Column]) -> (List[Column], str):
        """
        Add an extra row after the four rows.

        :param columns: The columns of words.

        """
        table = Table(columns[0],
                      columns[1],
                      columns[2],
                      False)
        paracol = r"\begin{paracol}{3}" + "\n"
        paracol_original = paracol[:]

        for column_name in ["left", "right"]:
            table, row = self.get_row(table, column_name, r"\switchcolumn[2]", paracol=paracol_original)
            paracol += row.text
            if column_name == "left":
                paracol += "\n\n\\switchcolumn[2]\n\n"
        paracol += "\n\n\\end{paracol}"

        # Update the columns.
        columns[0] = table.columns["left"]
        columns[1] = table.columns["center"]
        columns[2] = table.columns["right"]

        return columns, paracol

    def generate_paracol_table(self) -> (bool, str):
        """
        Generate paracol text. Returns the text and whether we're done.
        """

        col_tex = dict()
        # Get the shortest column.
        done, column_name, num_rows = self._get_shortest()
        if done:
            return True, ""

        # Generate the text of the shortest column.
        col_tex.update({column_name: self.generate_column_fast(column_name, num_rows)})

        # Generate the other column(s).
        for cn in ["left", "center", "right"]:
            if cn == column_name:
                continue
            tex = self.generate_column_slow(cn, num_rows)
            if tex != "":
                col_tex.update({cn: tex})

        if "left" in col_tex:
            if "center" in col_tex:
                if "right" in col_tex:
                    paracol = r"\begin{paracol}{3}"
                else:
                    paracol = r"\columnratio{" + Table.ONE_THIRD + "}\n" + r"\begin{paracol}{2}"
            elif "right" in col_tex:
                paracol = r"\begin{paracol}{2}"
            else:
                paracol = ""
        elif "center" in col_tex:
            if "right" in col_tex:
                paracol = r"\columnratio{" + Table.TWO_THIRDS + "}\n" + r"\begin{paracol}{2}"
            else:
                paracol = ""
        else:
            paracol = ""

        # Generate the table.
        tex_table = paracol[:]
        for col, i in zip(["left", "center", "right"], range(len(col_tex))):
            if col not in col_tex:
                continue
            tex_table += col_tex[col]
            if i < len(col_tex) - 1:
                tex_table += r"\switchcolumn" + "\n"
        if paracol != "":
            tex_table += "\n" + r"\end{paracol}" + "\n"
        return False, tex_table

    def generate_one_more_row(self) -> (bool, str):
        """
        Generate an extra row from the existing paracol structure. Returns true if we're done + the text.
        """

        if len([c for c in self.columns if len(c.words) > 0]) == 0:
            return True, ""

        table = Table(self.columns[0],
                      self.columns[1],
                      self.columns[2],
                      True)
        paracol = table.get_paracol_header()

        paracol_text = paracol[:]

        for column_name in table.columns:
            switch = table.get_switch_column(column_name)
            paracol_text += switch
            table, row = self.get_row(table, column_name, switch, paracol)
            paracol_text += row.text
        if paracol != "":
            paracol_text += "\n" + r"\end{paracol}" + "\n"
        return False, paracol_text

    def generate_column_fast(self, column_name: str, num_rows: int) -> str:
        """
        Generate a column and fill it with ALL of its word.
        This is best used to render the column with the least number of rows (since we know its width is static).

        :param column_name: The name of the column.
        :param num_rows: The number of rows we KNOW that this column has.
        """

        table = Table(self.columns[0],
                      self.columns[1],
                      self.columns[2],
                      False)

        paracol = table.get_paracol_header() + table.get_switch_column(column_name)

        col = table.columns[column_name]

        # Subtract words.
        last_row = list()

        done = False
        while not done:
            word = col.words.pop()

            num_rows_temp = self._get_num_rows_in_column(table.columns[column_name].words, paracol)

            # If, by removing this word, we removed the entire last row:
            # Try to first add a hyphenated fragment of that word.
            # If that doesn't work, re-add the whole word.
            if num_rows_temp < num_rows:
                done = True

                # Try to split the word.
                words = table.columns[column_name].words[:]
                got_hyphenated = False
                for pairs in word.get_hyphenated_pairs():
                    words.append(pairs[0])

                    # If we found a valid hyphenated pair:
                    # The last row gets the end fragment.
                    # The column gets the start fragment.
                    # Break, and start wrapping things up.
                    num_rows_temp_hyphen = self._get_num_rows_in_column(words, paracol)
                    if num_rows_temp_hyphen == num_rows_temp:
                        last_row.insert(0, pairs[1])
                        col.words.append(pairs[0])
                        got_hyphenated = True
                        break
                # Append the last word again.
                if not got_hyphenated:
                    col.words.append(word)
            else:
                last_row.insert(0, word)

        # Build the LaTeX text, minus the last row.
        col_tex = Row(self.state)
        for word in table.columns[column_name].words:
            col_tex, row_temp = self._add_word_to_row(col_tex, word)

        if len(last_row) > 0:
            # Buld the LaTeX text of the last row.
            last_row_tex = Row(self.state)
            for word in last_row:
                last_row_tex, row_temp = self._add_word_to_row(last_row_tex, word)
            last_row_tex.finish_tex()

            # Combine the text.
            tex = col_tex.text + r"\newline" + last_row_tex.text
        else:
            tex = col_tex.text

        # Delete the words.
        del table.columns[column_name].words[:]

        return tex

    def generate_column_slow(self, column_name: str, num_rows: int) -> str:
        """
        Generate a column inch by inch, row by row.

        :param column_name: The name of the column.
        :param num_rows: The target number of rows.
        """

        table = Table(self.columns[0],
                      self.columns[1],
                      self.columns[2],
                      False)

        if len(table.columns[column_name].words) == 0:
            return ""

        paracol = table.get_paracol_header() + table.get_switch_column(column_name)

        num_rows_now = 0
        rows = ""
        while num_rows_now < num_rows:
            table, row = self.get_row(table, column_name, "", paracol=paracol)
            rows += row.text
            num_rows_now += 1
            if num_rows_now < num_rows and rows != "":
                rows += r"\newline"
        return rows

    def _add_word_to_row(self, row: Row, word: Word) -> (Row, str):
        """
        Add a word to a row (or block of LaTeX text).
        Evaluate whether a current style (bold, italic, etc.) starts or stops.

        Return the row/text block with the new word and styling, and string WITH the styling but NOT the new word.

        :param row: The row.
        :param word: The new word.
        """

        # We'll modify a temporary copy of the row's text.
        row_temp = row.text[:]

        # Append the style to a temporary copy of the row.
        if word.start_bold:
            row_temp += self.bold_font
            self.state.bold = True
        if word.start_italic:
            row_temp += r"\textit{"
            self.state.italic = True
        if word.start_underline:
            row_temp += r"\underline{"
            self.state.underline = True

        # Append the new word.
        row_with_new_word = (row_temp + word.word + " ")

        if word.end_bold:
            row_with_new_word += "} "
            self.state.bold = False
        if word.end_italic:
            row_with_new_word += "} "
            self.state.italic = False
        if word.end_underline:
            row_with_new_word += "} "
            self.state.underline = False
        row_with_new_word = row_with_new_word.replace(" }", "}")

        return Row(self.state, text=row_with_new_word), row_temp

    def _get_next_word_in_row(self, row: Row, col: Column, paracol: str) -> (Row, Column, bool):
        """
        Append a new word, or a hyphenated fragment of a word, to the row. Returns the row, column, and whether we are done.

        :param row: The row being built.
        :param col: The column.
        :param paracol: The paracol header.
        """

        # Get the next word.
        word = col.words.pop(0)

        # Get the updated text.
        row_with_new_word, row_temp = self._add_word_to_row(row, word)

        # If there's more than 1 row, we'll need to subtract syllables.
        if self._generate_row_temp_pdf(row_with_new_word.text, paracol) > 1:
            for p in word.get_hyphenated_pairs():
                # Append the subword to the row.
                row_with_new_subword = row_temp + " " + p[0].word
                # We got a good subword!
                if self._generate_row_temp_pdf(row_with_new_subword, paracol) == 1:
                    # Finish the row.
                    row.text = row_with_new_subword
                    row.finish_tex()

                    # Append second subword to the col.
                    col.words.insert(0, p[1])
                    return row, col, True

            # We didn't find a good subword.
            # Re-append the word to the column.
            col.words.insert(0, word)

            # Finish the row.
            row.finish_tex()
            return row, col, True
        else:
            # If there's no more words, this row must be done.
            if len(col.words) == 0:
                row.text = row_with_new_word
                row.finish_tex()
                return row, col, True
            return row_with_new_word, col, False

    def _get_num_rows_in_column(self, words: List[Word], paracol: str) -> int:
        """
        Returns the number of rows in this column, if all words are included.

        :param words: The words in the column.
        :param paracol: The paracol header and \switchcolumn statements.
        """

        tex = Row(self.state)
        # Build the LaTeX text.
        for word in words:
            tex, row_temp = self._add_word_to_row(tex, word)
        # Get the number of lines of this column.
        return self._generate_row_temp_pdf(tex.text, paracol)

    def _generate_row_temp_pdf(self, tex: str, paracol: str) -> int:
        """
        Generate a pdf of just 1 row. Returns the actual number of rows.

        :param tex: The tex string.
        :param paracol: The paracol header.
        """

        lineno = r"\internallinenumbers \begin{linenumbers}" + Row.close_off_row(tex) + r"\end{linenumbers} \resetlinenumber[1]"

        # Temporarily close off the row.
        tex = paracol + lineno

        # End the paracol table.
        if paracol != "":
            tex += "\n" + r"\end{paracol}"

        # Generate a temporary pdf.
        self.generate_pdf(tex, "temp", False, True)

        # Get the number of rows.
        return self._get_num_rows("temp")

    def _get_shortest(self) -> (bool, str, int):
        """
        Get the shortest column. Returns (true if there are no columns left, the name of the column, the number of lines)
        """

        min_num_lines = math.inf
        min_column_name = ""

        table = Table(self.columns[0],
                      self.columns[1],
                      self.columns[2],
                      False)

        paracol = table.get_paracol_header()

        for column_name in table.columns:
            if len(table.columns[column_name].words) == 0:
                continue
            # Get the number of lines of this column.
            num_lines = self._get_num_rows_in_column(table.columns[column_name].words, paracol)
            if num_lines < min_num_lines:
                min_num_lines = num_lines
                min_column_name = column_name

            paracol += r"\switchcolumn"
        return math.isinf(min_num_lines), min_column_name, min_num_lines


if __name__ == "__main__":
    with io.open("test_page.md", "rt", encoding="utf-8") as f:
        test_page_text = f.read()

    left = ""
    center = ""
    right = ""

    q_col = ""

    for line in test_page_text.split("\n"):
        if line.startswith("## "):
            q_col = line[3:].lower()
        elif line.startswith("# ") or line == "":
            continue
        if q_col == "left":
            left = line
        elif q_col == "center":
            center = line
        elif q_col == "right":
            right = line
        else:
            raise Exception()

    Talmudifier(left, center, right).create()

# TODO output the final pdf.
