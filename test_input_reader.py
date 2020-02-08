import io
from talmudifier.talmudifier import Talmudifier


if __name__ == "__main__":
    # Read the test page.
    with io.open("test/test_input.md", "rt", encoding="utf-8") as f:
        txt = f.read()

    # Parse the test page into 3 columns.
    lines = txt.split("\n")
    left = lines[2]
    center = lines[6]
    right = lines[10]

    # Generate the PDF.
    t = Talmudifier(left, center, right)
    tex = t.get_chapter("Talmudifier Test Page") + "\n"
    tex += t.get_tex()
    doc = t.writer.write(tex, "test_page")

    # Output the LaTeX string used to generated the PDF as a .tex file.
    with io.open("Output/test_page.tex", "wt", encoding="utf-8") as f:
        f.write(doc)
