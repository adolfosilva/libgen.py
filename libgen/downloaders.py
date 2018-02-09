import abc
import os.path
from abc import ABC
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .exceptions import CouldntFindDownloadUrl
from .utils import random_string


class MirrorDownloader(ABC):
    def __init__(self, url: str, timeout: int = 10) -> None:
        """Constructs a new MirrorDownloader.

        :param url: URL from where to try to download file
        :param timeout: number of seconds for the download request to timeout
        :rtype: None
        """
        self.url = url
        self.timeout = timeout  # in seconds

    def download_publication(self, publication):
        """Downloads a publication from 'self.url'."""
        r = get(self.url, self.timeout)
        html = BeautifulSoup(r.text, 'html.parser')
        download_url = self.get_download_url(html)
        if download_url is None:
            raise CouldntFindDownloadUrl(self.url)
        filename = publication.filename()
        print(f"Downloading '{filename}'")
        data = get(download_url, self.timeout, stream=True)
        save_file(filename, data)

    @abc.abstractmethod
    def get_download_url(self, html) -> Optional[str]:
        """Returns the URL from where to download the
        file or None if it can't find the URL."""
        raise NotImplementedError


class LibgenIoDownloader(MirrorDownloader):
    """MirrorDownloader for 'libgen.io'."""
    def __init__(self, url: str) -> None:
        super().__init__(url)

    def get_download_url(self, html) -> Optional[str]:
        a = html.find('a', href=True, text='GET')
        return None if a is None else a.get('href')


class LibgenPwDownloader(MirrorDownloader):
    """MirrorDownloader for 'libgen.pw'."""
    def __init__(self, url: str) -> None:
        super().__init__(url)

    def get_download_url(self, html) -> Optional[str]:
        d = html.find('div', class_='book-info__download')
        if d is None:
            return None
        a = next(d.children, None)
        if a is None:
            return None
        return f"https://libgen.pw{a['href']}"


class BOkOrgDownloader(MirrorDownloader):
    """MirrorDownloader for 'b-ok.org'."""
    def __init__(self, url: str) -> None:
        super().__init__(url)

    def get_download_url(self, html) -> Optional[str]:
        a = html.find('a', class_='ddownload', href=True)
        return None if a is None else a.get('href')


class BookFiNetDownloader(MirrorDownloader):
    """MirrorDownloader for 'bookfi.net'."""
    def __init__(self, url: str) -> None:
        super().__init__(url)

    def get_download_url(self, html) -> Optional[str]:
        a = html.find('a', class_='ddownload', href=True)
        return None if a is None else a.get('href')


def get(url: str, timeout: int, stream: bool = False):
    """Sends an HTTP GET request.

    :param url: URL for the GET request
    :param timout: Number of seconds to timeout
    """
    return requests.get(url, stream=stream, timeout=timeout)


def save_file(filename: str, data: requests.models.Response):
    """Saves a file to the current directory."""
    try:
        with open(filename, 'wb') as f:
            for chunk in data.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Saved file as '{filename}'")
    except OSError as exc:
        if exc.errno == 36:  # filename too long
            (_, extension) = os.path.splitext(filename)  # this can fail
            # 'extension' already contains the leading '.', hence
            # there is no need for a '.' in between "{}{}"
            random_filename = f"{random_string(15)}{extension}"
            save_file(random_filename, data)
        else:
            raise  # re-raise if .errno is different then 36
    except Exception:
        raise
