import io
from talmudifier import Talmudifier


with io.open("test/test_input.md", "rt", encoding="utf-8") as f:
    txt = f.read()

lines = txt.split("\n")
left = lines[2]
center = lines[6]
right = lines[10]

t = Talmudifier(left, center, right)
tex = t.get_tex()
print(tex)
t.writer.write(tex, "markdown_input_test")
