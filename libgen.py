#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A short and sweet script to download books from libgen.in

A short and sweet script to download books from libgen.in."""

import abc
import itertools
import re
import sys
from abc import ABC
from typing import Generator, List
import argparse

import bs4
import requests
import tabulate
from bs4 import BeautifulSoup
from requests.exceptions import Timeout


class Book(object):
    def __init__(self, **kwargs) -> None:
        for (field, value) in kwargs.items():
            setattr(self, field, value)

    def _values(self) -> List[str]:
        fields = self._fields()
        return [getattr(self, f) for f in fields]

    def _fields(self) -> List[str]:
        return sorted([f for f in self.__dir__() if not f.startswith('_')])

    def __str__(self) -> str:
        fields = []
        for field in self._fields():
            value = getattr(self, field)
            f = str(field).capitalize() + ": " + str(value)
            fields.append(f)
        return ", ".join(fields)

class MirrorBookDownloader(ABC):
    def __init__(self, url: str, timeout: int = 10) -> None:
        self.url = url
        self.timeout = timeout # seconds

    @abc.abstractmethod
    def download_book(self):
        raise NotImplementedError

class LibgenIoDownloader(MirrorBookDownloader):
    def __init__(self, url: str) -> None:
        super().__init__(url)

    def download_book(self):
        r = get(self.url, self.timeout)
        html = BeautifulSoup(r.text, 'lxml')
        download_url = html.find('a', href=True, text='GET')['href']
        p = get(download_url, self.timeout, stream=True)
        filename = self.get_filename(p.headers)
        print('Downloading \'{}\''.format(filename))
        with open(filename, 'wb') as f:
            for chunk in p.iter_content(chunk_size=1024):
                if chunk: f.write(chunk)
        
    def get_filename(self, headers):
        r = re.search('filename="(.+)"', headers['Content-Disposition'])
        return r.group(1)

def get(url, timeout, stream=False):
    try:
        return requests.get(url, stream=stream, timeout=timeout)
    except Timeout:
        print('Error: Timeout at {} seconds'.format(timeout))
        sys.exit(1)

class Mirror(ABC):
    def __init__(self, search_url: str) -> None:
        self.search_url = search_url

    def run(self):
        for result_page in self.search(self.search_term):
            books = self.extract(result_page)
            selected = self.select(books)
            if selected:
                self.download(selected)
                # TODO: 'Downloaded X MB in Y seconds.'
                break

    def search(self, search_term: str) -> Generator[bs4.BeautifulSoup, None, None]:
        """
        Yield result pages for a given search term.

        :param term: the search term as a str
        :returns: BeautifulSoup4 object representing a result page
        """
        if len(search_term) < 3:
            raise ValueError('Your search term must be at least 3 characters long.')
        for page_url in self.next_page_url():
            print("Next results page: {}".format(page_url))
            r = requests.get(page_url)
            if r.status_code == 200:
                yield BeautifulSoup(r.text, 'lxml')

    @abc.abstractmethod
    def next_page_url(self) -> Generator[str, None, None]:
        """Yields the new results page."""
        raise NotImplementedError

    @abc.abstractmethod
    def extract(self, page) -> List[Book]:
        """Extract all the books info in a given result page.

        :param page: result page as an BeautifulSoup4 object
        :returns: list of books
        """
        raise NotImplementedError

    def select(self, books: List[Book]) -> Book:
        """
        Print the books info on a single search result page
        and allows the user to choose one to download.

        :param books: list of books
        :returns: a book as a dict or None if not found
        """
        headers = books[0]._fields()
        print(tabulate.tabulate([b._values() for b in books], headers, 'fancy_grid'))
        while True:
            try:
                choice = input('Choose book by ID: ')
                book = [b for b in books if b.id == choice]
                if not book:
                    raise ValueError
                else:
                    return book[0]
            except ValueError: print('Invalid choice. Try again.'); continue
            except (KeyboardInterrupt, EOFError): print(''); sys.exit(0)
            break

    # TODO: make it do parallel multipart download
    # http://stackoverflow.com/questions/1798879/download-file-using-partial-download-http
    def download(self, book):
        """
        Download a book from the mirror to the current directory.

        :param book: md5 hash of a book
        """
        for (_, mirror) in book.mirrors.items():
            mirror.download_book()


class GenLibRusEc(Mirror):
    search_url = "http://gen.lib.rus.ec/search.php?req="

    def __init__(self, search_term: str) -> None:
        super().__init__(self.search_url)
        self.search_term = search_term

    def next_page_url(self) -> Generator[str, None, None]:
        """Yields the new results page."""
        for pn in itertools.count(1):
            yield "{}{}&page={}".format(self.search_url, self.search_term, str(pn))

    def extract(self, page):
        """Extract all the books info in a given result page.

        :param page: result page as an BeautifulSoup4 object
        :returns: list of books as a list of dicts
        """
        r = re.compile("(.+)(\[(.+)\])?(.*)")
        trs = page.findAll('table')[2].findAll('tr')
        books = []
        for tr in trs[1:]:
            td = tr.findAll('td')
            fields = {}
            fields['id'] = td[0].text
            fields['authors'] = td[1].text.strip()
            t = r.search(td[2].text.strip())
            if t is None:
                fields['title'] = td[2].text.strip()
            else:
                fields['title'] = t.group(1).strip() 
                fields['edition'] = t.group(2)
                fields['isbn'] = t.group(3)
            fields['publisher'] = td[3].text
            fields['year'] = td[4].text
            fields['pages'] = td[5].text 
            fields['lang'] = td[6].text
            fields['size'] = td[7].text
            fields['extension'] = td[8].text
            fields['mirrors'] = {
                    'libgen.io': LibgenIoDownloader(td[9].findAll('a', href=True)[0]['href'])
                    #'libgen.pw': td[10].findAll('a', href=True)[0]['href'],
                    #'b-ok.org': td[11].findAll('a', href=True)[0]['href'],
                    #'bookfi.net': td[12].findAll('a', href=True)[0]['href']
            }
            books.append(Book(**fields))
        return books

class LibGenPw(Mirror):
    search_url = "http://gen.lib.rus.ec/search.php?req="

    def __init__(self, search_term: str) -> None:
        super().__init__(self.search_url)
        self.search_term = search_term

    def extract(self, page):
        pass

MIRRORS = {'http://gen.lib.rus.ec': GenLibRusEc}
           # 'https://libgen.pw': LibGenPw}

class NoAvailableMirrorError(Exception):
    """No mirrors are available to process request."""
    def __init__(self) -> None:
        msg = "No mirrors are available to process the request at this time."
        Exception.__init__(self, msg)

class MirrorFinder(object):
    def __init__(self) -> None:
        self.mirrors = MIRRORS

    def run(self, search_term: str):
        mirror = self.find_active_mirror()
        if mirror is None:
            raise NoAvailableMirrorError
        mirror(search_term).run()

    def find_active_mirror(self):
        for (homepage, mirror) in self.mirrors.items():
            r = requests.get(homepage)
            if r.status_code == 200:
                return mirror
        return None

def main():
    parser = argparse.ArgumentParser(description='Read more, kids.')
    parser.add_argument('-s', '--search', dest='search', required=True, help='search term')
    args = parser.parse_args()
    MirrorFinder().run(args.search)


if __name__ == '__main__':
    main()
