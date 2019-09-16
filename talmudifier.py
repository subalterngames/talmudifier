from pathlib import Path
import re
from typing import List
from sys import platform
from os import devnull
from os.path import join, exists
import math
import io
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
            font_size = ""
        else:
            font_size = "\\fontsize{" + str(font_data["size"]) + "}{" + str(font_data["skip"]) + "}"

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
                style.bold = False

            if w.startswith("_"):
                style.italic = True
            elif w.endswith("_"):
                style.italic = False

            if w.startswith("_**") or w.startswith("**_"):
                style.bold = True
                style.italic = True
            elif w.endswith("_**") or w.endswith("**_"):
                style.bold = False
                style.italic = False

            if "<u>" in w:
                style.underline = True
            elif "</u>" in w:
                style.underline = False

            # Append the new word.
            words.append(Word(w, Style(style.bold, style.italic, style.underline), substitutions, citation))

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

        return Column(words, "\\" + column_name + "font", font_size)

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

    def run(self):
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
        
        print(tex)

Talmudifier("Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
            "There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don't look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn't anything embarrassing hidden in the middle of text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, injected humour, or non-characteristic words etc.",
            "Fusce ac lacus faucibus, gravida metus ut, ullamcorper nulla. Duis orci quam, hendrerit volutpat est eu, aliquet blandit augue. Fusce semper lorem vitae consectetur pretium. Duis id suscipit est. Etiam lorem enim, fringilla vel nunc eget, hendrerit sodales neque. Sed condimentum rhoncus commodo. Aenean imperdiet lectus eget efficitur fringilla. Nulla magna risus, congue et eros nec, ultrices molestie metus. Praesent ultrices mauris purus, nec commodo orci posuere ut. Donec augue sem, tincidunt sit amet elementum a, accumsan ut quam. Duis luctus diam leo, et convallis justo congue ac. Curabitur at tellus nisi. Cras dignissim consequat magna sed vulputate. Donec at enim sed sem dictum fermentum.").run()