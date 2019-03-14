from libgen.downloaders import filter_filename


def test_filter_filename():
    filename = 'Русский язык (1962) - ####автор@.djvu'
    assert filter_filename(filename) == 'Русский язык (1962) - автор.djvu'
