from pathlib import Path
from typing import List
from json import load
from column import Column
from util import to_camelcase
import io
from typing import Optional
from pdf_writer import PDFWriter
from citation import Citation
from word import Word
from style import Style
from row_maker import RowMaker
from paracol import Paracol


class Talmudifier:
    def __init__(self, text_left: str, text_center: str, text_right: str, recipe_filename="default.json"):
        # Read the recipe.
        recipe_path = Path(f"recipes/{recipe_filename}")
        if not recipe_path.exists():
            print(f"Couldn't find recipe: {recipe_filename}; using default.json instead.")
        with io.open(str(recipe_path.resolve()), "rt", encoding="utf-8") as f:
            self.recipe = load(f)

        # Read the preamble.
        assert Path("header.txt").exists()
        with io.open("header.txt", "rt", encoding="utf-8") as f:
            preamble = f.read()

        # Append font declarations.
        for col_name in ["left", "center", "right"]:
            preamble += "\n" + self._get_font_declaration(col_name)

            # Append a citation font declaration, if any.
            citation_declaration = self._get_citation_font_declaration(col_name)
            if citation_declaration is not None:
                preamble += "\n" + citation_declaration

        # Append color declarations.
        if "colors" in self.recipe:
            for color in self.recipe["colors"]:
                preamble += "\n\\definecolor{" + color + "}{HTML}{" + self.recipe["colors"][color] + "}"

        # Append the chapter command.
        assert "chapter" in self.recipe, "Chapter not found in recipe."
        assert "definition" in self.recipe["chapter"], "Chapter definition not found."
        preamble += "\n" + self.recipe["chapter"]["definition"]

        # Append additional definitions.
        if "misc_definitions" in self.recipe:
            for d in self.recipe["misc_definitions"]:
                preamble += "\n" + d

        # Create the PDF writer.
        self.writer = PDFWriter(preamble)

        self.left = self._get_column(text_left, "left")
        self.center = self._get_column(text_center, "center")
        self.right = self._get_column(text_right, "right")

    def _get_font_declaration(self, column_name: str) -> str:
        """
        Returns the font declaration in the recipe associated with the column.

        :param column_name: The name of the column (left, center, right).
        """

        # Check that all required keys are present.
        assert "fonts" in self.recipe, "No fonts found in recipe!"
        assert column_name in self.recipe["fonts"], f"No fonts found for: {column_name}"
        font_data = self.recipe["fonts"][column_name]
        for required_key in ["path", "ligatures", "regular_font"]:
            assert required_key in font_data, f"Required key in {column_name} not found: {required_key}"

        # Append a / to the path if needed.
        path = font_data['path']
        if not path.endswith("/"):
            path += "/"

        declaration = f"\\newfontfamily\\{column_name}font[Path={path}, Ligatures={font_data['ligatures']}"

        # Add styles to the declaration.
        for style_key in ["italic_font", "bold_font", "bold_italic_font"]:
            if style_key in font_data:
                declaration += f", {to_camelcase(style_key)}={font_data[style_key]}"

        # Finish the declaration and add the regular font.
        declaration += "]{" + font_data["regular_font"] + "}"
        return declaration

    def _get_citation_font_declaration(self, column_name: str) -> Optional[str]:
        """
        Returns the font declaration for a citation. May be none.

        :param column_name: The name of the column associated with the citation.
        """

        # Check that all required keys are present.
        assert "fonts" in self.recipe, "No fonts found in recipe!"
        assert column_name in self.recipe["fonts"], f"No fonts found for: {column_name}"
        font_data = self.recipe["fonts"][column_name]

        # Check if there is a citation.
        if "citation" not in font_data:
            return None

        citation_data = font_data["citation"]
        for required_key in ["path", "font", "font_command", "pattern"]:
            assert required_key in citation_data, f"Required key in citation {column_name} not found: {required_key}"

        # Append a / to the path if needed.
        path = citation_data['path']
        if not path.endswith("/"):
            path += "/"

        return "\\newfontfamily" + citation_data["font_command"] + "[Path=" + path + "]{" + citation_data["font"] + "}"

    def _get_column(self, text: str, column_name: str) -> Column:
        """
        Returns a column of words and font commands.

        :param text: The raw markdown text.
        :param column_name: The name of the column.
        """

        # Check that all required keys are present.
        assert "fonts" in self.recipe, "No fonts found in recipe!"
        assert column_name in self.recipe["fonts"], f"No fonts found for: {column_name}"
        font_data = self.recipe["fonts"][column_name]

        # Get the font-size command.
        if "skip" not in font_data or "size" not in font_data:
            font_size = -1
            font_skip = -1
        else:
            font_size = font_data["size"]
            font_skip = font_data["skip"]

        # Get the citation.
        if "citation" in font_data:
            citation = Citation(font_data["citation"])
        else:
            citation = None

        # Get the substitutions.
        if "substitutions" in font_data:
            substitutions = font_data["substitutions"]
        else:
            substitutions = None

        word_str = text.split(" ")
        words = []

        style = Style(False, False, False)

        for w in word_str:
            if w.startswith("**"):
                style.bold = True
            elif w.endswith("**"):
                style.bold = True

            if w.startswith("_"):
                style.italic = True
            elif w.endswith("_"):
                style.italic = True

            if w.startswith("_**") or w.startswith("**_"):
                style.bold = True
                style.italic = True
            elif w.endswith("_**") or w.endswith("**_"):
                style.bold = True
                style.italic = True

            if "<u>" in w:
                style.underline = True
            elif "</u>" in w:
                style.underline = True

            w_str = w.replace("*", "").replace("_", "").replace("<u>", "").replace("</u>", "")

            # Append the new word.
            words.append(Word(w_str, Style(style.bold, style.italic, style.underline), substitutions, citation))

            # Check if this was one word, e.g. **this** and apply styles again.
            if w.endswith("**"):
                style.bold = False
            if w.endswith("_"):
                style.italic = False
            if w.endswith("_**") or w.endswith("**_"):
                style.bold = False
                style.italic = False
            if "</u>" in w:
                style.underline = False

        return Column(words, "\\" + column_name + "font", font_size, font_skip)

    def _get_expected_length(self, column_name: str, width: str, num_rows: int) -> int:
        """
        Get the expected length of a given number of rows of a given column of a given width.

        :param column_name: The name of the column.
        :param width: The width, e.g. half.
        :param num_rows: The number of rows.
        """

        # Check that all required keys are present.
        assert "fonts" in self.recipe, "No fonts found in recipe!"
        assert column_name in self.recipe["fonts"], f"No fonts found for: {column_name}"

        if "character_counts" not in self.recipe:
            return -1
        if width not in self.recipe["character_counts"]:
            return -1

        if column_name not in self.recipe["character_counts"][width]:
            return -1

        counts = self.recipe["character_counts"][width][column_name]
        if str(num_rows) in counts:
            return counts[str(num_rows)]
        else:
            if "1" in counts:
                return counts["1"] * num_rows
            else:
                return -1

    def _get_four_rows_left_right(self, column: Column, column_name: str) -> (str, Column):
        """
        Build four rows on the left or right.

        :param column: The column.
        :param column_name: The name of the column.
        :return:
        """

        # Build 4 rows of the left and right columns.
        rowmaker = RowMaker(True, False, True, column_name, self.writer)
        return rowmaker.get_text_of_length(column, 4, self._get_expected_length(column_name, "one_third", 4))

    def _get_one_row_left_right(self, column: Column, column_name: str) -> (str, Column):
        # Build 1 row of the left and right columns.
        rowmaker = RowMaker(True, True, True, column_name, self.writer)
        return rowmaker.get_text_of_length(column, 1, self._get_expected_length(column_name, "one_third", 1))

    def _get_column_width(self, target: str) -> str:
        if len(self.left.words) > 0:
            if len(self.center.words) > 0:
                if len(self.right.words) > 0:
                    return "one_third"
                else:
                    if target == "left":
                        return "one_third"
                    else:
                        return "two_thirds"
            elif len(self.right.words) > 0:
                return "half"
            else:
                return ""
        elif len(self.center.words) > 0:
            if len(self.right.words) > 0:
                if target == "center":
                    return "two_thirds"
                else:
                    return "one_third"
            else:
                return ""
        else:
            return ""

    def _get_column_name(self, col: Column) -> str:
        """
        Returns the name of the column.

        :param col: The column.
        """

        if col == self.left:
            return "left"
        elif col == self.center:
            return "center"
        elif col == self.right:
            return "right"
        else:
            raise Exception("Couldn't match column.")

    def _get_columns_with_words(self) -> List[Column]:
        """
        Returns a list of columns that have words.
        """

        return [c for c in [self.left, self.center, self.right] if len(c.words) > 0]

    def _get_shortest(self) -> (Column, str, int, bool):
        """
        Returns which of my columns is the shortest, its name, the number of lines, and whether any has any lines.
        """

        # Check if any columns have any words.
        cols = self._get_columns_with_words()
        if len(cols) == 0:
            return None, "", 0, False
        elif len(cols) == 1:
            return cols[0], "", -1, True

        min_col = None
        min_lines = 10000000
        min_column_name = ""

        for col in cols:
            column_name = self._get_column_name(col)

            # Create the row maker.
            rowmaker = RowMaker(self.left in cols, self.center in cols, self.right in cols, column_name, self.writer)

            # Get the number of lines.
            num_lines = rowmaker.get_num_rows(col.get_tex(True))

            # Get the number of lines relative to the left column's font size.
            num_lines = int((col.font_size / self.left.font_size) * num_lines)

            if num_lines < min_lines:
                min_col = col
                min_lines = num_lines
                min_column_name = column_name

        return min_col, min_column_name, min_lines, True

    def get_tex(self) -> str:
        tex = ""

        # Get four row on the left and on the right.
        left_tex, self.left = self._get_four_rows_left_right(self.left, "left")
        right_tex, self.right = self._get_four_rows_left_right(self.right, "right")

        # Add the paracol environment.
        tex += "\n\\begin{paracol}{2}\n\n" + left_tex + "\\switchcolumn" + right_tex + "\n\n\\end{paracol}\n\n"

        # Get four row on the left and on the right.
        left_tex, self.left = self._get_one_row_left_right(self.left, "left")
        right_tex, self.right = self._get_one_row_left_right(self.right, "right")

        # Add the paracol environment.
        tex += "\n\\begin{paracol}{3}\n\n" + left_tex + "\\switchcolumn[2]" + right_tex + "\n\n\\end{paracol}\n\n"
        
        done = False
        while not done:
            shortest_col, shortest_col_name, num_lines, any_lines = self._get_shortest()
            done = not any_lines
            if done:
                continue

            # Just fill the page with the last column's words.
            if num_lines == -1:
                tex += "\n\n\\begin{paracol}{1}\n\n" + shortest_col.get_tex(True) + "\n\n\\end{paracol}\n\n"
                done = True
                continue

            # Start building the table.
            table = {shortest_col_name: shortest_col.get_tex(True)}

            assert self.left == shortest_col or self.center == shortest_col or self.right == shortest_col

            paracol = Paracol.get_paracol_header(len(self.left.words) > 0, len(self.center.words) > 0, len(self.right.words) > 0)

            # Fill the other columns, if possible.
            cols = self._get_columns_with_words()
            has_left = self.left in cols
            has_center = self.center in cols
            has_right = self.right in cols

            for i in range(len(cols)):
                if cols[i] == shortest_col:
                    continue
                col_name = self._get_column_name(cols[i])

                # Build the column.
                rm = RowMaker(has_left, has_center, has_right, col_name, self.writer)

                # Set the target number of lines based on the font size relative to the left column.
                target_num_lines = int((self.left.font_size / cols[i].font_size) * num_lines + 1)

                col_tex, col = rm.get_text_of_length(cols[i],
                                                     target_num_lines,
                                                     self._get_expected_length(col_name,
                                                                               self._get_column_width(col_name),
                                                                               target_num_lines))

                # Update the table.
                table.update({col_name: col_tex})

                # Update my columns.
                if col_name == "left":
                    self.left = col
                elif col_name == "center":
                    self.center = col
                elif col_name == "right":
                    self.right = col
                else:
                    raise Exception()

            # Empty the shortest column.
            shortest_col.words = []

            # Build the paracol.
            for col_key in ["left", "center", "right"]:
                if col_key not in table:
                    continue
                paracol += table[col_key]
                if col_key != "right":
                    paracol += "\n\n\\switchcolumn\n\n"

            # End the paracol.
            paracol += "\n\n\\end{paracol}\n\n"

            # Add the paracol.
            tex += paracol

        return tex

    def get_chapter(self, title: str) -> str:
        """
        Returns the chapter command.

        :param title: The title of the chapter.
        """

        assert "chapter" in self.recipe, "Chapter not found in recipe."
        assert "command" in self.recipe["chapter"], "Chapter command not found in recipe."
        assert "numbering" in self.recipe["chapter"], "Chapter numbering not found in recipe."

        chapter = "\\chapter"
        if not self.recipe["chapter"]["numbering"]:
            chapter += "*"
        chapter += "{" + self.recipe["chapter"]["command"] + "{" + title + "}}"
        return chapter
