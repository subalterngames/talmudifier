from hyphen import Hyphenator


class Word:
    """
    A word is a string plus style metadata (bold, italic, etc.)
    """

    H = Hyphenator('en_US')

    def __init__(self, word: str, bold: bool, italic: bool, underline: bool, smallcaps: bool, citation: bool,
                 margin_note=None):
        """
        :param word: The actual word, stripped of any markdown styling.
        :param bold: If true, this word is bolded.
        :param italic: If true, this word is italicized.
        :param underline: If true, this word is underlined.
        :param smallcaps: If true, this word is in smallcaps.
        :param citation: If true, this word is a citation.
        :param margin_note: The margin note, if any.
        """

        self.word = word
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.smallcaps = smallcaps
        self.citation = citation
        self.margin_note = margin_note

    def get_hyphenated_pairs(self) -> list:
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
                # Add the margin note only to the first fragment.
                margin_note = self.margin_note if p == p0 else None
                w = Word(p, self.bold, self.italic, self.underline, self.smallcaps, self.citation, margin_note)

                h.append(w)
            pairs.append(h)
        return pairs

    def get_margin_note(self) -> str:
        """
        Returns the margin note text.
        """

        if self.margin_note:
            return r"\marginnote{\justifying \tiny " + self.margin_note + "}"
        else:
            return ""
