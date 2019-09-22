import re
from pathlib import Path


"""
Use this script to generate documentation from Python scripts.
"""


def get_function_documentation(header_line, index, lines):
    started = False

    # Get the name of the function.
    function_name = re.match("def (.*):", header_line).group(1)

    function_description = []
    parameters = dict()
    return_description = ""
    for i in range(index + 1, len(lines)):
        line = lines[i].strip()
        if line == '"""':
            if started:
                break
            else:
                started = True
        elif line == "":
            continue
        elif line.startswith(":param"):
            param_split = line[7:].split(":")
            parameters.update({param_split[0]: param_split[1]})
        elif line.startswith(":return"):
            return_description = line[8:]
        else:
            function_description.append(line)
    return function_name, function_description, parameters, return_description


def get_file_description(lines):
    began_description = False
    description = ""
    for line in lines:
        line = line.strip()
        if line == '"""':
            if began_description:
                description += "\n***\n\n"
                return description
            else:
                began_description = True
        else:
            if began_description:
                description += line.strip() + "\n"


if __name__ == "__main__":
    files = ["talmudifier.py"]

    output_directory = Path("")
    if not output_directory.exists():
        output_directory.mkdir()

    # Create documentation for each Python file in the list.
    for python_file in files:
        doc = "# " + python_file + "\n\n"

        lines = Path(python_file).read_text().split("\n")
        doc += get_file_description(lines)

        get_file_description(lines)

        for line, i in zip(lines, range(len(lines))):
            line = line.strip()
            # Found a new function.
            if line.startswith("def "):
                f_n, f_d, p, r_d = get_function_documentation(line, i, lines)
                if f_n[0] == "_" and not f_n.startswith("__init__"):
                    continue
                # Append the name of the function.
                doc += "### `" + f_n + "`\n\n"
                # Append the description of the function.
                for description_line in f_d:
                    doc += description_line + "\n"
                doc += "\n\n"
                if len(p) > 0:
                    doc += "| Parameter | Description |\n| --- | --- |\n"
                    for parameter in p:
                        doc += "| " + parameter + " | " + p[parameter] + "|\n"
                    doc += "\n"
                if r_d != "":
                    doc += "_Returns:_ " + r_d + "\n\n***\n\n"
                else:
                    doc += "***\n\n"

        output_filename = python_file[:-3] + ".md"
        output_directory.joinpath(output_filename).write_text(doc)
