from talmudifier.talmudifier import Talmudifier
from argparse import ArgumentParser
from pathlib import Path


class HammerOfLilith:
    def __init__(self, line: int):
        """
        :param line: The line number of the paragraph.
        """

        # Get the Hammer Of Lilith root directory.
        self.hol_dir = Path.home().joinpath("HammerOfLilith")
        assert self.hol_dir.exists(), f"Directory not found: {self.hol_dir.resolve()}"

        self.line = line

    def _get_text(self, filename: str) -> str:
        p = self.hol_dir.joinpath(f"book/{filename}")
        assert p.exists(), f"File not found: {p.resolve()}"
        return p.read_text(encoding="utf-8")

    def get_paragraph(self, filename: str) -> str:
        """
        Returns the paragraph text at the line.
        """

        return self._get_text(filename).split("\n")[self.line - 1]


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("line", type=int, help="The line number.", nargs="?", default=7)
    args = parser.parse_args()

    hol = HammerOfLilith(args.line)

    center = hol.get_paragraph("book_of_lilith.md")
    left = hol.get_paragraph("mishnah.md")
    right = hol.get_paragraph("you.md")

    # Create the page and output the pdf.
    tex = Talmudifier(left, center, right).create_pdf(output_filename=f"hol_{args.line}")

    # Output the text.
    Path(f"Output/hol_{args.line}.tex").write_text(tex, encoding='utf-8')
