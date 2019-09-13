from talmudifier import Word, Column


# Test word styles.
w = Word("Rabbi", False)
assert w.word == "Rabbi"
assert not w.bold
assert not w.underline
assert not w.italic
assert not w.smallcaps

w = Word("Rabbi", True)
assert w.word == "Rabbi"
assert not w.bold
assert not w.underline
assert not w.italic
assert w.smallcaps

w = Word("**Rabbi**", False)
assert w.word == "Rabbi"
assert w.bold
assert not w.underline
assert not w.italic
assert not w.smallcaps

w = Word("_Rabbi_", False)
assert w.word == "Rabbi"
assert not w.bold
assert not w.underline
assert w.italic
assert not w.smallcaps

w = Word("_**Rabbi**_", False)
assert w.word == "Rabbi"
assert w.bold
assert not w.underline
assert w.italic
assert not w.smallcaps

w = Word(r"<u>Rabbi<\u>", False)
assert w.word == "Rabbi"
assert not w.bold
assert w.underline
assert not w.italic
assert not w.smallcaps

w = Word(r"<u>_**Rabbi**_<\u>", False)
assert w.word == "Rabbi"
assert w.bold
assert w.underline
assert w.italic
assert not w.smallcaps

w = Word(r"<u>_**`Rabbi`**_<\u>", False)
assert w.word == "Rabbi"

w = Word(r"<u>_**Rabbi**_<\u>", True)
assert w.word == "Rabbi"
assert w.bold
assert w.underline
assert w.italic
assert w.smallcaps

# Test hypnenation.
w = Word(r"<u>_**California**_<\u>", False)
pairs = w.get_hyphenated_pairs()
assert len(pairs) == 3
for p in pairs:
    assert len(p) == 2
    for h in p:
        assert h.bold == w.bold
        assert h.italic == w.italic
        assert h.underline == w.underline
        assert h.smallcaps == w.smallcaps
    assert p[0].word not in w.word
    assert p[0].word[:-1] in w.word
    assert p[1].word in w.word

w = Word("Bob", False)
pairs = w.get_hyphenated_pairs()
assert len(pairs) == 0