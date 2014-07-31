#!/usr/bin/env python

"""A short and sweet script to download books from libgen.org

A short and sweet script to download books from libgen.org."""

import re
import sys
import math
import urllib2
import argparse
from bs4 import BeautifulSoup

searchurl = 'http://libgen.org/search.php?&req=%s&view=simple&column=def&sort=title&sortmode=ASC&page=%d'
downloadurl = 'http://libgen.org/get.php?md5='

# make it do parallel multipart download
# http://stackoverflow.com/questions/1798879/download-file-using-partial-download-http

def _number_of_result_pages(numberofbooks, resultsperpage):
    return int(math.ceil(numberofbooks / float(resultsperpage)))

def _next_page(term, numberofbooks):
    for n in range(1, _number_of_result_pages(numberofbooks, 25) + 1):
        yield searchurl % (term, n)

def search(term):
    """
    Yields a result page for a given search term.

    :param term: the search term as a str
    :returns: a BeautifulSoup4 object representing a result page 
    """
    if len(term) < 4:
        raise ValueError('Your search term must be at least 4 characters long.')
    firstpage = BeautifulSoup(urllib2.urlopen(searchurl % (term, 1)))
    numberofbooks = int(re.search('\d+', firstpage.find(text=re.compile('^\d+ books found'))).group())
    print(('%d books found' % numberofbooks))
    for page in _next_page(term, numberofbooks):
        yield BeautifulSoup(urllib2.urlopen(page))

# def extract(page):
#     """Return a list of md5 hashes corresponding to each book found on a single search page."""
#     data = BeautifulSoup(page)
#     print(data.find(text=re.compile("^\d+ books found"))
#     # data.find_all(href=re.compile("book/index.php\?md5="))

def select(resultpage):
    """
    Prints the books on a single search result page and
    allows the user to choose which one to download.

    :param books: list of 
    """
    pass

def download(book):
    """
    Downloads a book from libgen to the current directory.

    :param book: an md5 hash of a book as a str
    """
    r = urllib2.urlopen(downloadurl + book)
    filename = re.search('filename=\"(.+)\"', r.info()['Content-Disposition']).group(1)
    with open(filename, 'wb') as f:
        meta = r.info()
        file_size = int(meta.getheaders("Content-Length")[0])
        print("Downloading: %s\nSize: %.2f MB" % (' - '.join(filename.split('-')[:2]), float(file_size) / 10**6))

        file_size_dl = 0
        block_sz = 1024
        while True:
            buf = r.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buf)
            f.write(buf)
            status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
            status = status + chr(8)*(len(status)+1)
            print status,


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read more, kids.')
    parser.add_argument('-s', '--search', dest='search', required=True, help='search term')
    parser.add_argument('-y', '--year', dest='year', type=int, help='year of publication')
    parser.add_argument('-t', '--type', dest='extension', default='pdf', help='file extension')
    args = parser.parse_args()

    # make search function a generator so that we can do this:
    # for result_page in search(args.search):
    #     extract(result_page)     
    #     reduce(extractaccumulate, search(options.search))
    #     reduce(lambda a, b: extract(a) + extract(b), search(options.search)) 
    # extract(search(sys.argv[1]))
    # download("6738829E0C619C853DFE3507C80BCE98")
    for page in search(args.search):
        print page.prettify()

    # 'Downloaded X MB in Y seconds.'
