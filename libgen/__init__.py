# -*- coding: utf-8 -*-

"""
libgen
~~~~~~

Download books from 'gen.lib.rus.ec', 'libgen.io',
'libgen.pw', 'b-ok.org' and 'bookfi.net'."""


from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __status__, __author__, __author_email__, __license__
from .__version__ import __copyright__

from .__main__ import MIRRORS as AVAILABLE_MIRRORS
from .__main__ import MirrorFinder
