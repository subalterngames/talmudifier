# Recipes

A recipe is a JSON file that defines the fonts and other styling rules for your page. It is functionally the same as just writing your own TeX preamble, but probably a lot more user-friendly.

By default, `talmudifier.py` uses: `recipes/default.json`.

All custom recipes should be saved to the `recipes/` directly as `.json` files.

## `fonts`

Definitions for the font per column.

```json
"fonts":
{
    "left":
    {
        
    }
}
```

_Key = The name of the font (left, center, right). Don't change these._

| Field              | Type       | Description                                                  | Required? |
| ------------------ | ---------- | ------------------------------------------------------------ | --------- |
| `path`             | string     | Path to the directory of fonts relative to `talmudifier.py`. | ✔         |
| `ligatures`        | string     | How ligatures are handled. This should probably always be `"TeX"`. There are other options, but the documentation for them is [sparse](https://tex.stackexchange.com/questions/296737/what-do-the-various-values-of-the-ligatures-option-of-fontspec-do). | ✔         |
| `regular_font`     | string     | The regular font file. Must be a file located in the directory `path`. | ✔         |
| `italic_font`      | string     | The _italic_ font file. Must be a file located in the directory `path`. | ❌         |
| `bold_font`        | string     | The **bold** font file. Must be a file located in the directory `path`. | ❌         |
| `bold_italic_font` | string     | The _**bold+italic**_ font file. Must be a file located in the directory `path`. | ❌         |
| `size`             | integer    | The font size. This will default to whatever the font size is in the `header.txt` preamble. If `skip` is not included, this is ignored. | ❌         |
| `skip`             | integer    | The size of the spacing between two lines. Generally you want this to be 2 more than `size`. If `size` is not included, this is ignored. | ❌         |
| `substitutions`    | dictionary | Per word in this column, replace every key in the dictionary with the value. | ❌         |
| `citation`         | dictionary | The recipe for citations _pointing to_ this column. See below. | ❌         |

#### `citation`

Citations are letters or words that direct the reader from column to column.

| Field          | Type              | Description                                                  | Required? |
| -------------- | ----------------- | ------------------------------------------------------------ | --------- |
| `path`         | string            | Path to the directory of fonts relative to `talmudifier.py`. | ✔         |
| `font`         | string            | The font file. Must be a file located in the directory `path`. | ✔         |
| `command`      | string            | The command used in the TeX document body to start the citation font. This can be the same as `font_command` but you might want to define a custom version. `default.json` _does_ have a custom version, that makes citations red-colored. | ✔         |
| `font_command` | string            | The command used to name the font family. You probably don't want to change this from `default.json`'s values. | ✔         |
| `pattern`      | string<br>(regex) | `talmudifier.py` will replace anything in the input string with this regex pattern with a properly-formatted citation letter. | ✔         |

## `character_counts`

These are the average number of characters in a column across many trials, given different column configurations (e.g. left and right only), a target column (e.g. left), and a target number of rows (e.g. 1).

`talmudifier.py` will use these numbers to fill columns with a "best guess" number of words before adding and subtracting words to reach a given row number target (e.g. if there are only left and right columns and you want 1 row on the left, `talmudifier.py` will first try to fill the row with 47 characters). If there is no key present, `talmudifier.py` will first look for the `"1"` key and multiply the value by the number of rows (e.g. 47 * 4). If there are no keys at all, `talmudifier.py` will just add a word at a time to the column (which is much slower).

You can calculate these values yourself by running `row_length_calculator.py`.

```json
  "character_counts":
  {
    "LR":
    {
      "left":
      {
        "1": 47
      }
    }
  }
```

| Key      | Description                                                  |
| -------- | ------------------------------------------------------------ |
| `"LR"`   | The columns in this table. Can be `"LCR"`, `"LR"`, etc.      |
| `"left"` | The target column within the table. Can be `"left"`, `"center"`, or `"right"`. |
| `"1"`    | The target number of rows. Must be an integer.<br>Value=The average number of characters across many trials. |

#### `row_length_calculator.py`

Use this script to calculate the average number of characters per row given a recipe, a list of tables, and a target column.

| Argument    | Type    | Description                                                  | Default        |
| ----------- | ------- | ------------------------------------------------------------ | -------------- |
| `--columns` | string  | The columns in the table. Can be `LCR`, `LR`, etc.           | `LR`           |
| `--target`  | string  | The target column. Can be `"left"`, `"center"`, or `"right"`. |                |
| `--rows`    | integer | The number of rows.                                          | `1`            |
| `--trials`  | integer | The number of trials to run and then average.                | `100`          |
| `--recipe`  | string  | Filename of the recipe file in the `recipes/` directory.     | `default.json` |

## `chapter`

Define the chapter header style.

| Field        | Type    | Description                                                  | Required? |
| ------------ | ------- | ------------------------------------------------------------ | --------- |
| `definition` | string  | The TeX definition of the command used to define the font. Sorry this is a bit of a mess. The parameter after `\newcommand` must match `\command` (see `default.json`). | ✔         |
| `command`    | string  | The command used when creating a chapter.                    | ✔         |
| `numbering`  | boolean | If true, chapter headers will start with numbers.            | ✔         |

## `colors`

Define colors for the preamble. The key is the name of the color, and the value is the HTML hex code. This can be left empty if you don't need any extra colors.

## `misc_definitions`

Anything else you'd like to include in the preamble. `default.json` includes the following:

- Definitions for left and right citation font commands; note how they include a color found in `colors`.
- Definition for `\flowerfont`, referred to in `recipe["fonts"]["left"]["substitutions"]`.