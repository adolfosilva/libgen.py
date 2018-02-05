#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from libgen import MirrorFinder


def main():
    parser = argparse.ArgumentParser(description='Read more, kids.')
    parser.add_argument('-s', '--search', dest='search', required=True, help='search term')
    args = parser.parse_args()
    MirrorFinder().run(args.search)

main()
