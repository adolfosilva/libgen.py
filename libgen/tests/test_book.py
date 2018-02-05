from libgen import Book


def test_book_initalization():
    state = {'id': 5, 'author': 'Fernando Pessoa'}
    b = Book(**state)
    assert b.id == 5
    assert b.author == 'Fernando Pessoa'

