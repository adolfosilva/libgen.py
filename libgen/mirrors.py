import abc
import copy
import itertools
import re
import sys
from abc import ABC
from typing import Any, Dict, Generator, List, Optional, Tuple

import bs4
import requests
import tabulate
from bs4 import BeautifulSoup
from requests.exceptions import Timeout

from . import downloaders
from .exceptions import CouldntFindDownloadUrl, NoResults
from .publication import Publication

RE_ISBN = re.compile(
    r"(ISBN[-]*(1[03])*[ ]*(: ){0,1})*" +
    r"(([0-9Xx][- ]*){13}|([0-9Xx][- ]*){10})"
)

RE_EDITION = re.compile(r"(\[[0-9] ed\.\])")


class Mirror(ABC):

    def __init__(self, search_url: str) -> None:
        self.search_url = search_url

    @staticmethod
    def get_href(cell) -> Optional[str]:
        links = cell.find_all('a', href=True)
        first = next(iter(links), None)
        return None if first is None else first.get('href')

    @staticmethod
    # @ensure('length of each value list in values is the same has the number of header values', lambda r: all(map(lambda x: len(x) == len(r[0]), r[1])))
    def get_headers_values(publications: List[Publication]) -> Tuple[List[str], List[List[Any]]]:
        # headers should not include 'mirrors'
        headers = set()
        values = []
        for p in publications:
            # we deep copy the publication's attributes because
            # we need to remove the key 'mirrors' from the attributes
            # and that's a destructive operation, but we don't want to
            # change the publication, we really only want a list of
            # attribute names
            attrs = copy.deepcopy(p.attributes)
            attrs.pop('mirrors', None)
            headers.update(set(attrs))  # set of keys from attrs
            values.append(list(attrs.values()))
        return (list(headers), values)

    def run(self):
        try:
            for publications in self.search():
                selected = self.select(publications)
                if selected:
                    self.download(selected)
                    # TODO: 'Downloaded X MB in Y seconds.'
                    break
        except NoResults as e:
            print(e)

    def search(self, start_at: int = 1) -> Generator[bs4.BeautifulSoup, None, None]:
        """
        Yield result pages for a given search term.

        :param start_at: results page to start at
        :returns: BeautifulSoup4 object representing a result page
        """
        if len(self.search_term) < 3:
            raise ValueError('Your search term must be at least 3 characters long.')

        print(f"Searching for: '{self.search_term}'")

        for page_url in self.next_page_url(start_at):
            r = requests.get(page_url)
            if r.status_code == 200:
                publications = self.extract(BeautifulSoup(r.text, 'html.parser'))

                if not publications:
                    raise NoResults
                else:
                    yield publications

    @abc.abstractmethod
    def next_page_url(self, start_at: int) -> Generator[str, None, None]:
        """Yields the new results page."""
        raise NotImplementedError

    @abc.abstractmethod
    def extract(self, page) -> List[Publication]:
        """Extract all the results info in a given result page.

        :param page: result page as an BeautifulSoup4 object
        :returns: list of :class:`Publication` objects
        """
        raise NotImplementedError

    def select(self, publications: List[Publication]) -> Publication:
        """
        Print the search results and asks the user to choose one to download.

        :param publications: list of Publication
        :returns: a Publication
        """
        headers, values = Mirror.get_headers_values(publications)
        print(tabulate.tabulate(values, headers, 'fancy_grid'))
        while True:
            try:
                choice = input('Choose publication by ID: ')
                publications = [p for p in publications if p.id == choice]
                if not publications:
                    raise ValueError
                else:
                    return publications[0]
            except ValueError:
                print('Invalid choice. Try again.')
                continue
            except (KeyboardInterrupt, EOFError) as e:
                print(e)
                sys.exit(1)
            break

    # TODO: make it do parallel multipart download
    # http://stackoverflow.com/questions/1798879/download-file-using-partial-download-http
    def download(self, publication):
        """
        Download a publication from the mirror to the current directory.

        :param publication: a Publication
        """
        for (n, mirror) in publication.mirrors.items():
            # print(f"About to try {n}\n")
            try:
                mirror.download_publication(publication)
                break  # stop if successful
            except (CouldntFindDownloadUrl, Timeout) as e:
                print(e)
                print("Trying a different mirror.")
                continue
            except Exception:
                import traceback
                print(f"An error occurred: {sys.exc_info()[0]}")
                print(traceback.format_exc())
                print("Trying a different mirror.")
                continue
            print("Failed to download publications.")


class GenLibRusEc(Mirror):
    search_url = "http://gen.lib.rus.ec/search.php?req="

    def __init__(self, search_term: str) -> None:
        super().__init__(self.search_url)
        self.search_term = search_term

    def next_page_url(self, start_at: int) -> Generator[str, None, None]:
        """Yields the new results page."""
        for pn in itertools.count(start_at):
            yield f"{self.search_url}{self.search_term}&page={str(pn)}"

    def extract(self, page):
        """Extract all the publications info in a given result page.

        :param page: result page as an BeautifulSoup4 object
        :returns: list of Publication
        """
        rows = page.find_all('table')[2].find_all('tr')
        results = []
        for row in rows[1:]:
            cells = row.find_all('td')
            attrs = self.extract_attributes(cells)
            results.append(Publication(attrs))
        return results

    def extract_attributes(self, cells) -> Dict[str, Any]:
        attrs = {}
        attrs['id'] = cells[0].text
        attrs['authors'] = cells[1].text.strip()

        # The 2nd cell contains title information
        # In best case it will have: Series - Title - Edition - ISBN
        # But everything except the title is optional
        # and this optional text shows up in green font
        for el in cells[2].find_all('font'):
            et = el.text
            if RE_ISBN.search(et) is not None:
                # A list of ISBNs
                attrs['isbn'] = [
                    RE_ISBN.search(N).group(0)
                    for N in et.split(",")
                    if RE_ISBN.search(N) is not None
                ]
            elif RE_EDITION.search(et) is not None:
                attrs['edition'] = et
            else:
                attrs['series'] = et

            # Remove this element from the DOM
            # so that it isn't considered a part of the title
            el.extract()

        # Worst case: just fill everything in the title field
        attrs['title'] = cells[2].text.strip()

        attrs['publisher'] = cells[3].text
        attrs['year'] = cells[4].text
        attrs['pages'] = cells[5].text
        attrs['lang'] = cells[6].text
        attrs['size'] = cells[7].text
        attrs['extension'] = cells[8].text

        libgen_io_url = Mirror.get_href(cells[9])
        libgen_pw_url = Mirror.get_href(cells[10])
        bok_org_url = Mirror.get_href(cells[11])
        bookfi_net_url = Mirror.get_href(cells[12])

        # TODO: each of these _url can be None
        attrs['mirrors'] = {
                'libgen.io': downloaders.LibgenIoDownloader(libgen_io_url),
                'libgen.pw': downloaders.LibgenPwDownloader(libgen_pw_url),
                'b-ok.org': downloaders.BOkOrgDownloader(bok_org_url),
                'bookfi.net': downloaders.BookFiNetDownloader(bookfi_net_url)
        }
        return attrs


class LibGenPw(Mirror):
    search_url = "http://gen.lib.rus.ec/search.php?req="

    def __init__(self, search_term: str) -> None:
        super().__init__(self.search_url)
        self.search_term = search_term

    def extract(self, page):
        # TODO: implement
        raise NotImplementedError


MIRRORS = {'http://gen.lib.rus.ec': GenLibRusEc,
           'https://libgen.pw': LibGenPw}
"""
Dictionary of available mirrors from where to download files.
"""
