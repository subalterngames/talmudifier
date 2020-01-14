from hyphen import Hyphenator
from typing import Dict, Optional
from talmudifier.style import Style
from talmudifier.citation import Citation
import re


class Word:
    """
    A word is a string plus style metadata (bold, italic, etc.)
    """

    H = Hyphenator('en_US')

    def __init__(self, word: str,
                 style: Style,
                 substitutions: Optional[Dict[str, str]],
                 citation: Optional[Citation],
                 get_pairs=True):
        """
        :param word: The actual word, stripped of any markdown styling.
        :param style: The font style for this word.
        :param substitutions: A list of keys to replace for values to make a valid TeX string.
        :param get_pairs: If true, get pairs of hyphenated fragments.
        """

        self.word = word
        self.pairs = []

        # Try to make this word a citation. If it is a citation, stop right here (citations are never hyphenated).
        if citation is not None:
            self.word, self.is_citation = citation.apply_citation_to(self.word)
        else:
            self.is_citation = False

        if self.is_citation:
            self.style = Style(False, False, False)
            return
        else:
            self.style = style

        # Get the pairs.
        if get_pairs:
            self.pairs = self._get_hyphenated_pairs(substitutions)

        # Do the substitutions.
        if substitutions is not None:
            for key in substitutions:
                self.word = re.sub(key, substitutions[key], self.word)

        if word.startswith('"'):
            self.word = "``" + word[1:]
        elif word. startswith("'"):
            self.word = "`" + word[1:]

    def _get_hyphenated_pairs(self, substitutions: Dict[str, str]) -> list:
        """
        Get all possible hyphenated pairs of this word (e.g. Cal- ifornia).
        """

        try:
            pairs_text = self.H.pairs(self.word)
        except IndexError:
            return []

        pairs = []

        for pair in pairs_text:
            # Append the hyphen to the first word.
            p0 = pair[0] + "-"
            p1 = pair[1]
            h = []

            # Add pairs of Word objects.
            for p in [p0, p1]:
                w = Word(p, self.style, substitutions if p == p0 else None,
                         None,
                         get_pairs=False)

                h.append(w)
            pairs.append(h)
        return pairs

    @staticmethod
    def is_valid(word: str) -> bool:
        """
        Returns true if the word is valid. Invalid words include characters that are illegal in TeX.
        There might not be a way to make this list exhaustive! We shall see...

        :param word: The word string.
        """

        return word not in ["}", "{", "[", "]", "\\", "|", "*", "**", "***"]
