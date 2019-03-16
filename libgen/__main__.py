import argparse

import requests

from .exceptions import NoAvailableMirror
from .mirrors import MIRRORS


class MirrorFinder(object):
    def __init__(self) -> None:
        self.mirrors = MIRRORS

    def run(self, search_term: str, non_interactive: bool):
        """Tries to find an active mirror and runs the search on it."""
        try:
            mirror = self.find_active_mirror()
            if mirror is None:
                raise NoAvailableMirror
            mirror(search_term).run(non_interactive)
        except NoAvailableMirror as e:
            print(e)

    # TODO: eliminate this method
    # Maybe use the chain of responsability pattern
    def find_active_mirror(self):
        for (homepage, mirror) in self.mirrors.items():
            r = requests.get(homepage)
            if r.status_code == 200:
                return mirror
        return None


def main():
    p = argparse.ArgumentParser(description='Read more, kids.')
    p.add_argument('-s', '--search', dest='search', required=True, help='search term')
    p.add_argument('-n', '--non-interactive', dest='non_interactive', help='non interactive mode, download first available choice', action='store_true', default=False)
    args = p.parse_args()
    MirrorFinder().run(args.search, args.non_interactive)


if __name__ == '__main__':
    main()
