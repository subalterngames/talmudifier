# talmudifier.py

Generate Talmud-esque page layouts, given markdown plaintext and a recipe JSON file.

***

### `__init__(self, text_left: str, text_center: str, text_right: str, recipe_filename="default.json")`



| Parameter | Description |
| --- | --- |
| text_left |  The markdown text of the left column.|
| text_center |  The markdown text of the center column.|
| text_right |  The markdown text of the right column.|
| recipe_filename |  The filename of the recipe, located in recipes/|

***

### `get_tex(self) -> str`

Generate the body of text.
1. Create 4 rows on the left and right (width = one half).
2. Create 1 row on the left and right (width = one third).
3. Until the columns are all done: Find the shortest column and add it. Add other columns up to that length.


***

### `get_chapter(self, title: str) -> str`

Returns the chapter command.


| Parameter | Description |
| --- | --- |
| title |  The title of the chapter.|

***

### `create_pdf(self, output_filename="output", print_tex=False) -> str`

Create a PDF. Generate the chapter and the body, and append them to the preamble. Returns the LaTeX string.


| Parameter | Description |
| --- | --- |
| output_filename |  The name of the output file.|
| print_tex |  If true, print the LaTeX string to the console.|

***

