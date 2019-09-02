from subprocess import call
from pathlib import Path
from sys import platform
from os import devnull
from talmudifier.util import output_directory


class PDFWriter:
    """
    Given LaTeX text, write a PDF.
    """

    END_DOCUMENT = r"\end{sloppypar}\end{document}"

    def __init__(self, preamble_filename="header.txt", font_commands=None):
        """
        :param preamble_filename: The name of the file containing the preamble text.
        :param font_commands: Additional font commands. May be none.
        """

        preamble_path = Path(preamble_filename)
        assert preamble_path.exists(), f"Preamble file not found: {preamble_path}"
        self.preamble = Path(preamble_filename).read_text()

        for font_command in font_commands:
            self.preamble += font_command + "\n"

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

        # Generate the PDF.
        if platform == "linux":
            call(
                ["pdflatex",
                 "-output-format", "pdf",
                 "-output-directory", output_directory,
                 "-jobname", filename, doc],
                stdout=open(devnull, "wb"))
        else:
            call('latex -output-format=pdf -output-directory ' +
                 output_directory + ' -job-name=' + filename + " " + doc + " -quiet")

        assert Path(output_directory).joinpath(filename).exists(), f"Failed to create: {filename}"

        return doc_raw