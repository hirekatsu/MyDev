# -*- coding: utf8 -*-

import pprint


class _UnicodePrint(pprint.PrettyPrinter):
    """
    DO NOT USE. A hidden class for unicode print.
    """
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return object.encode('utf8'), True, False
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)

unicodeprint = _UnicodePrint()
