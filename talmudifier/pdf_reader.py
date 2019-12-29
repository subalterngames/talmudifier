from os.path import exists
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.layout import LAParams
import io


class PDFReader:
    """
    Extracts the raw text of a PDF and reads it.
    """

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> str:
        """
        Source: http://www.blog.pythonlibrary.org/2018/05/03/exporting-data-from-pdfs-with-python/
        """

        # Added by me.
        assert exists(pdf_path), f"{pdf_path} does not exist."

        resource_manager = PDFResourceManager()
        fake_file_handle = io.StringIO()
        converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
        page_interpreter = PDFPageInterpreter(resource_manager, converter)

        with open(pdf_path, 'rb') as fh:
            for page in PDFPage.get_pages(fh,
                                          caching=True,
                                          check_extractable=True):
                page_interpreter.process_page(page)

            text = fake_file_handle.getvalue()

        # close open handles
        converter.close()
        fake_file_handle.close()

        return text

    @staticmethod
    def get_num_rows(pdf_path: str) -> int:
        """
        Returns the number of rows in a PDF file.
        This assumes that the PDF was created with LaTeX with the lineno package.

        :param pdf_path: The filepath to the PDF file.
        """

        text = PDFReader.extract_text_from_pdf(pdf_path)

        # Get the line numbers.
        lines = text.split("\n")
        lines = [line for line in lines if line.isdigit()][:-1]

        if len(lines) > 0:
            return int(lines[-1])
        else:
            return 1
