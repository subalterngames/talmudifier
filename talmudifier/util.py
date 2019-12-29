from pathlib import Path
import re


# Set and create the output directory.
output_directory = Path("Output")
if not output_directory.exists():
    output_directory.mkdir()
output_directory = str(output_directory.resolve())


def to_camelcase(s: str) -> str:
    """
    Converts underscore_strings to UpperCamelCaseStrings.
    Source: https://rodic.fr/blog/camelcase-and-snake_case-strings-conversion-with-python/

    :param s: The string.
    """

    return re.sub(r'(?:^|_)(\w)', lambda m: m.group(1).upper(), s)
