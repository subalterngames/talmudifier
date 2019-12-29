import re


class Citation:
    """
    The rules defining a citation in a column.
    """

    def __init__(self, data: dict):
        """
        :param data: The citation data dictionary (see default.json).
        """

        assert "command" in data, "No command found"
        assert "pattern" in data, "No pattern found"

        # Set the command to start the citation and the pattern to search for.
        self.command = data["command"]
        self.pattern = data["pattern"]

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
