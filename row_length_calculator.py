from word import Word
from pdf_writer import PDFWriter
from pdf_reader import PDFReader
from style import Style
from random import shuffle
from tqdm import tqdm


class RowLengthCalculator:
    def __init__(self, num_columns: int, font: str):
        self.paracol = "\\begin{paracol}{" + str(num_columns) + "}\n\n\\fontsize{11}{13}" + font
        self.writer = PDFWriter()

    def _get_num_rows(self, line: str, word: Word) -> int:
        tex = r"\internallinenumbers \begin{linenumbers}" + line + " " + word.word + r"\end{linenumbers} \resetlinenumber[1]"
        tex = self.paracol + tex + "\n\n\\end{paracol}\\end{sloppypar}\\end{document}"
        self.writer.write(tex, "line_count")
        return PDFReader.get_num_rows("/home/seth/talmudifier/Output/line_count.pdf")

    def _get_num_characters_in_trial(self, josephus: list, style: Style) -> int:
        line = ""

        random_words = josephus[:]
        shuffle(random_words)

        # Build a row of random words.
        done = False
        while not done:
            word = Word(random_words.pop(), style, None, None)

            num_lines = self._get_num_rows(line, word)

            if num_lines == 1:
                line += " " + word.word
            # We went over the end. Try to get a hyphenated fragment.
            else:
                pairs = word.pairs
                for pair in pairs:
                    for p in pair:
                        num_lines = self._get_num_rows(line, p)
                        if num_lines == 1:
                            line += " " + word.word
                            return len(line)

                done = True
        return len(line)

    def get_num_chars(self, num_trials: int) -> int:
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
    print(RowLengthCalculator(2, r"\leftfont").get_num_chars(1000))
