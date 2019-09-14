class Style:
    """
    A style (e.g. bold) for a font.
    """

    def __init__(self, bold: bool, italic: bool, underline: bool):
        """
        :param bold: This style is bolded.
        :param italic: This style is italicized.
        :param underline: This style is underlined.
        """

        self.bold = bold
        self.italic = italic
        self.underline = underline
