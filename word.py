from hyphen import Hyphenator
from typing import Dict, Optional
from style import Style
from citation import Citation


class Word:
    """
    A word is a string plus style metadata (bold, italic, etc.)
    """

    H = Hyphenator('en_US')

    def __init__(self, word: str,
                 style: Style,
                 substitutions: Dict[str, str],
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
        self.word, self.is_citation = citation.apply_citation_to(self.word)
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
                self.word = self.word.replace(key, substitutions[key])

    def _get_hyphenated_pairs(self, substitutions: Dict[str, str]) -> list:
        """
        Get all possible hyphenated pairs of this word (e.g. Cal- ifornia).
        """

        pairs_text = self.H.pairs(self.word)
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
