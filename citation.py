import re


class Citation:
    """
    The rules defining a citation in a column.
    """

    def __init__(self, data: dict):
        """
        :param data: The citation data dictionary (see default.json).
        """

        assert "path" in data, "No path to font found."
        assert "font" in data, "No font found"
        assert "command" in data, "No command found"
        assert "pattern" in data, "No pattern found"
        assert "font_command" in data, "No font command found"
        assert data["font"].endswith(".ttf") or data["font"].endswith(".otf"), "Font name must end in .ttf or .otf"

        # Set the path and add a / if needed.
        path = data["path"]
        if not path.endswith("/"):
            path += "/"

        # Set the command to start the citation and the pattern to search for.
        self.command = data["command"]
        self.pattern = data["pattern"]

        # Get the definition.
        self.definition = r"\newfontfamily" + data["font_command"] + "[Path=" + path + "]{" + data["font"] + "}"

    def apply_citation_to(self, word: str) -> (str, bool):
        """
        If this word is a citation, apply the citation.

        :param word: The string.
        :return: (The modified word, True if the word was modified)
        """

        match = re.match(self.pattern, word)
        if match is not None:
            return self.command + "{" + match.group(1) + "}", True
        else:
            return word, False
