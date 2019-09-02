from talmudifier.util import output_directory
from os.path import join, exists
from PyPDF2 import PdfFileReader


class PDFReader:
    """
    Extracts the raw text of a PDF and reads it.
    """

    @staticmethod
    def get_num_rows(filename: str) -> int:
        """
        Returns the number of rows in a PDF file.
        This assumes that the PDF was created with LaTeX with the lineno package.

        :param filename: The name of the file.
        """

        path = join(output_directory, filename + ".pdf")

        assert exists(path), f"{path} does not exist."

        # Extract the number of lines
        with open(path, "rb") as f:
            pdf = PdfFileReader(f)
            extracted_text = pdf.getPage(pdf.getNumPages() - 1).extractText()

        lines = extracted_text.split("\n")
        assert len(lines) >= 4, "Not enough lines. Did you include the lineno package?"

        lineno = lines[-3]

        assert lineno.isdigit(), f"Expected a line number but got: {lineno}. Did you include the lineno package?"
        return int(lineno)
