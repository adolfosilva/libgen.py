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
    return ((searchurl % (term, n)) for n in range(2, _number_of_result_pages(numberofbooks, 25) + 1))

def _range(start, stop, step):
    return [(n, min(n+step, stop)) for n in range(start, stop, step)]

def _parts(request, ranges):
    return ((request % (a,b)) for a, b in ranges)

def search(term):
    """
    Yield result pages for a given search term.

    :param term: the search term as a str
    :returns: BeautifulSoup4 object representing a result page
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

def select(books):
    """
    Print the books on a single search result page and
    allows the user to choose one to download.

    :param books: list of books
    """
    for book in books:
        print('{0}. {1} {2} {3}'.format(book['id'], book['author'], book['title'], book['publisher'])),
        print('{0} {1} {2} {3} {4}'.format(book['year'], book['pages'], book['lang'], book['size'], book['extension']))
    while True:
        try:
            choice = int(raw_input('Choose book: '))
            if choice <= 0 or choice > 25:
                raise ValueError
        except ValueError: print('Invalid choice. Try again.'); continue
        except (KeyboardInterrupt, EOFError): print(''); sys.exit(0)
        break
    return next((b for b in books if b['id'] == choice), None)

def download(book):
    """
    Download a book from libgen.org to the current directory.

    :param book: md5 hash of a book
    """
    r = urllib2.urlopen(downloadurl + book)
    filename = re.search('filename=\"(.+)\"', r.info()['Content-Disposition']).group(1)
    with open(filename, 'wb') as f:
        filesize = int(r.info().getheaders("Content-Length")[0])
        print("Downloading: %s\nSize: %.2f MB" % (' - '.join(filename.split('-')[:2]), float(filesize) / 10**6))

        filesize_dl = 0
        block_sz = 1024
        while True:
            buf = r.read(block_sz)
            if not buffer:
                break
            filesize_dl += len(buf)
            f.write(buf)
            status = r"%10d  [%3.2f%%]" % (filesize_dl, filesize_dl * 100. / filesize)
            status = status + chr(8)*(len(status)+1)
            print status,

def download2(book):
    """
    Download a book from libgen.org to the current directory.

    :param book: a md5 hash of a book
    """
    blocksize = 1024 # bytes
    req = urllib2.Request(downloadurl + book)
    req.headers['Range'] = 'bytes=%s-%s' % (start, end)
    parts = list(_parts('bytes=%s-%s', _range(0, filesize, blocksize)))
    r = urllib2.urlopen(req)
    filename = re.search('filename=\"(.+)\"', r.info()['Content-Disposition']).group(1)
    with open(filename, 'wb') as f:
        filesize = int(r.info().getheaders("Content-Length")[0])
        print("Downloading: %s\nSize: %.2f MB" % (' - '.join(filename.split('-')[:2]), float(filesize) / 10**6))

        filesize_dl = 0
        while True:
            buf = r.read(blocksize)
            if not buffer:
                break
            filesize_dl += len(buf)
            f.write(buf)
            status = r"%10d  [%3.2f%%]" % (filesize_dl, filesize_dl * 100. / filesize)
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
    download2("6738829E0C619C853DFE3507C80BCE98")
    #for page in search(args.search):
    #    print page.prettify()

    # 'Downloaded X MB in Y seconds.'
