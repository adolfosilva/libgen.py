from libgen.exceptions import NoAvailableMirror
from libgen.mirrors import MIRRORS

import argparse

import requests


class MirrorFinder(object):
    def __init__(self) -> None:
        self.mirrors = MIRRORS

    def run(self, search_term: str):
        """Tries to find an active mirror and runs the search on it."""
        try:
            mirror = self.find_active_mirror()
            if mirror is None:
                raise NoAvailableMirror
            mirror(search_term).run()
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
    args = p.parse_args()
    MirrorFinder().run(args.search)


if __name__ == '__main__':
    main()
