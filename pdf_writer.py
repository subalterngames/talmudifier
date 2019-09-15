from subprocess import call
from pathlib import Path
from sys import platform
from os import devnull
from util import output_directory


class PDFWriter:
    """
    Given LaTeX text, write a PDF.
    """

    END_DOCUMENT = r"\end{sloppypar}\end{document}"

    def __init__(self, preamble_filename="header.txt"):
        """
        :param preamble_filename: The name of the file containing the preamble text.
        """

        preamble_path = Path(preamble_filename)
        assert preamble_path.exists(), f"Preamble file not found: {preamble_path}"
        self.preamble = Path(preamble_filename).read_text()

        # Begin the document.
        self.preamble += r"\begin{document}\begin{sloppypar}" + "\n\n"

    def write(self, text: str, filename: str) -> str:
        """
        Create a PDF from LaTeX text.

        :param text: The LaTeX text.
        :param filename: The filename of the PDF.
        :return: The LaTeX text, including the preamble and the end command(s).
        """

        # Combine the preamble, the new text, and the end command(s).
        doc_raw = self.preamble + text + PDFWriter.END_DOCUMENT

        # Replace line breaks with spaces.
        doc = doc_raw.replace("\n", " ")

        # Verify that all curly braces are balanced.
        num_start = len([c for c in doc if c == "{"])
        num_end = len([c for c in doc if c == "}"])
        assert num_start == num_end, f"Unbalanced curly braces!\n\n{doc_raw}"

        # Generate the PDF.
        if platform == "linux":
            call(
                ["xelatex",
                 "-output-directory", str(Path(output_directory).resolve()),
                 "-jobname", filename, doc],
                stdout=open(devnull, "wb"))
        else:
            call('latex -output-format=pdf -output-directory ' +
                 output_directory + ' -job-name=' + filename + " " + doc + " -quiet")

        assert Path(output_directory).joinpath(filename + ".pdf").exists(), f"Failed to create: {filename}"

        return doc_raw
