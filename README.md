## Fonts

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

#### Citation

Citations are letters or words that direct the reader from column to column.

| Field          | Type              | Description                                                  | Required? |
| -------------- | ----------------- | ------------------------------------------------------------ | --------- |
| `path`         | string            | Path to the directory of fonts relative to `talmudifier.py`. | ✔         |
| `font`         | string            | The font file. Must be a file located in the directory `path`. | ✔         |
| `command`      | string            | The command used in the TeX document body to start the citation font. This can be the same as `font_command` but you might want to define a custom version. `default.json` _does_ have a custom version, that makes citations red-colored. | ✔         |
| `font_command` | string            | The command used to name the font family. You probably don't want to change this from `default.json`'s values. | ✔         |
| `pattern`      | string<br>(regex) | `talmudifier.py` will replace anything in the input string with this regex pattern with a properly-formatted citation letter. | ✔         |

