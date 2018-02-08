from libgen.publication import Publication


def test_pub_initialization():
    attrs = {'id': 5, 'author': 'Fernando Pessoa'}
    p = Publication(attrs)
    assert p.id == 5
    assert p.author == 'Fernando Pessoa'
    assert p.title is None


def test_pub_attributes():
    attrs = {'id': 5, 'author': 'Fernando Pessoa'}
    p = Publication(attrs)
    assert p.attributes == attrs.keys()


def test_pub_values():
    attrs = {'id': 5, 'author': 'Fernando Pessoa'}
    p = Publication(attrs)
    assert list(p.values()) == list(attrs.values())


def test_pub_repr():
    attrs = {'id': 5, 'author': 'Fernando Pessoa'}
    p = Publication(attrs)
    assert repr(p) == 'Publication(\'id\': 5, \'author\': Fernando Pessoa)'
