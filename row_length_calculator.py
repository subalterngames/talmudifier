from word import Word
from pdf_writer import PDFWriter
from pdf_reader import PDFReader
from style import Style
from random import shuffle
from tqdm import tqdm
from paracol import Paracol
from argparse import ArgumentParser
from json import load


class RowLengthCalculator:
    """
    Calculate the average number of characters in a given number of rows.
    """

    def __init__(self, columns: str, target: str, font: str, font_size: str, num_rows: int):
        """
        :param columns: The columns included in this paracol environment as a string, e.g. "LC"
        :param target: The target column, e.g. "left"
        :param font: The font command, e.g. "\\leftfont"
        :param font_size: The font size command, e.g. "\\fontsize{11}{13}"
        :param num_rows: The number of rows to make.
        """

        self.paracol = Paracol.get_paracol_header("L" in columns, "C" in columns, "R" in columns)
        switch = Paracol.get_switch_from_left("L" in columns, "C" in columns, "R" in columns, target)
        self.paracol += "\n\n" + switch
        self.paracol += "\n\n" + font_size + font
        self.writer = PDFWriter()
        self.num_rows = num_rows

    def _get_num_rows(self, line: str, word: Word) -> int:
        """
        Returns the number of rows if the word was added to the line.

        :param line: The line.
        :param word: The new word.
        """
        tex = r"\internallinenumbers \begin{linenumbers}" + line + " " + word.word + r"\end{linenumbers} \resetlinenumber[1]"
        tex = self.paracol + tex + "\n\n\\end{paracol}"
        self.writer.write(tex, "line_count")
        return PDFReader.get_num_rows("/home/seth/talmudifier/Output/line_count.pdf")

    def _get_num_characters_in_trial(self, josephus: list, style: Style) -> int:
        """
        Fill a row with random words from Josephus' Antiquities, and return the number of characters.
        Try to fill the row as much as possible by adding a hyphenated fragment at the end.

        :param josephus: Random words from Antiquities.
        :param style: The font style (regular).
        """

        line = ""

        random_words = josephus[:]
        shuffle(random_words)

        # Build a row of random words.
        done = False
        while not done:
            word = Word(random_words.pop(), style, None, None)

            num_lines = self._get_num_rows(line, word)

            # We went over the end. Try to get a hyphenated fragment.
            if num_lines > self.num_rows:
                pairs = word.pairs
                for pair in pairs:
                    for p in pair:
                        num_lines = self._get_num_rows(line, p)
                        if num_lines == self.num_rows:
                            line += " " + p.word
                            return len(line.strip())
                done = True
            else:
                line += " " + word.word
        return len(line.strip())

    def get_num_chars(self, num_trials: int) -> int:
        """
        Get the average number of characters over the course of many trials.

        :param num_trials: The number of trials.
        """

        num_chars_total = 0

        pbar = tqdm(total=num_trials)

        # Get some words.
        with open("test/josephus.txt", "rt") as f:
            josephus = f.read()
        josephus = josephus.split(" ")
        josephus = [j for j in josephus if j != ""]

        style = Style(False, False, False)

        for i in range(num_trials):
            num_chars_total += self._get_num_characters_in_trial(josephus, style)
            pbar.update(1)
            pbar.set_description(str(round(num_chars_total / (i + 1))))
        pbar.close()

        return round(num_chars_total / num_trials)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--columns", type=str)
    parser.add_argument("--target", type=str)
    parser.add_argument("--rows", nargs="?", default=1, type=int)
    parser.add_argument("--trials", nargs="?", default=100, type=int)
    parser.add_argument("--recipe", nargs="?", default="default.json")

    args = parser.parse_args()

    # Load the recipe
    with open("recipes/" + args.recipe, "rt") as f:
        recipe = load(f)
    if args.target == "left":
        font = r"\leftfont"
    elif args.target == "center":
        font = r"\centerfont"
    elif args.target == "right":
        font = r"\rightfont"
    else:
        raise Exception(f"Invalid target: {args.target}")

    size = r"\fontsize{" + str(recipe["fonts"][args.target]["size"]) + "}{" + str(recipe["fonts"][args.target]["skip"]) + "}"

    num_chars = RowLengthCalculator(args.columns, args.target, font, size, args.rows).get_num_chars(args.trials)
    print(f"Cols: {args.columns}\nTarget: {args.target}\nRows: {args.rows}\nAVERAGE: {num_chars}")
