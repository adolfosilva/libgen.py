from libgen.publication import Publication


def test_pub_initialization():
    attrs = {'id': 5, 'authors': 'Fernando Pessoa'}
    p = Publication(attrs)
    assert p.id == 5
    assert p.authors == 'Fernando Pessoa'
    assert p.title is None


def test_pub_fields():
    attrs = {'id': 5, 'authors': 'Fernando Pessoa'}
    p = Publication(attrs)
    assert p.fields == attrs.keys()


def test_pub_values():
    attrs = {'id': 5, 'authors': 'Fernando Pessoa'}
    p = Publication(attrs)
    assert list(p.values) == list(attrs.values())


def test_pub_repr():
    attrs = {'id': 5, 'authors': 'Fernando Pessoa'}
    p = Publication(attrs)
    assert repr(p) == 'Publication(\'id\': 5, \'authors\': Fernando Pessoa)'


def test_pub_len():
    attrs = {'id': 5, 'authors': 'Fernando Pessoa'}
    p = Publication(attrs)
    assert len(p) == len(attrs)


def test_pub_filename_no_extension():
    p = Publication({'id': 5, 'authors': 'Fernando Pessoa'})
    assert p.filename() is None


def test_pub_filename_extension_only():
    p = Publication({'id': 5,
                     'authors': 'Fernando Pessoa',
                     'extension': 'pdf'})
    assert p.filename().endswith('.pdf')


def test_pub_filename_extension_and_title():
    p = Publication({'id': 5,
                     'title': 'Island',
                     'extension': 'pdf'})
    assert p.filename() == 'Island.pdf'


def test_pub_filename_extension_title_and_year():
    p = Publication({'id': 5,
                     'title': 'Island',
                     'year': 1962,
                     'extension': 'epub'})
    assert p.filename() == 'Island (1962).epub'


def test_pub_filename_extension_title_authorss_and_year():
    p = Publication({'id': 5,
                     'title': 'Island',
                     'authors': 'Aldous Huxley',
                     'year': 1962,
                     'extension': 'djvu'})
    assert p.filename() == 'Island (1962) - Aldous Huxley.djvu'
