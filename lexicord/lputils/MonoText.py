# -*- coding: utf-8 -*-
import sys
import codecs
import re
import unicodedata

class MonoText(list):
    """
    Stores and manipulates a collection of text (segments).
    """
    _re_crlf = re.compile(r'[\r\n]', re.M)
    _re_trim_begin = re.compile(r'^\s+', re.M)
    _re_trim_end = re.compile(r'\s+$', re.M)
    _re_trim_consecutive = re.compile(r'\s{2,}', re.M)
    @staticmethod
    def trimtext(text, beginning=True, ending=True, consecutive=False):
        if beginning:
            text = MonoText._re_trim_begin.sub('', text)
        if ending:
            text = MonoText._re_trim_end.sub('', text)
        if consecutive:
            text = MonoText._re_trim_consecutive.sub(' ', text)
        return text

    def __init__(self, seq=()):
        super(MonoText, self).__init__(seq)

    def readtext(self, filename, encoding=sys.getdefaultencoding(), metatextparser=None):
        self.__init__()
        if not metatextparser:
            metatextparser = lambda x: x
        with codecs.open(filename, 'r', encoding=encoding) as f:
            self.__init__(metatextparser(l.strip()) for l in f)
        return self

    def writetext(self, filename, encoding=sys.getdefaultencoding(), metatextparser=None, start=None, end=None):
        if not metatextparser:
            metatextparser = lambda x: x
        if start is None:
            start = 0
        if end is None:
            end = len(self)
        with codecs.open(filename, 'w', encoding=encoding) as f:
            i = 0
            for s in self:
                if i >= start:
                    f.write(metatextparser(s) + '\n')
                i += 1
                if i >= end:
                    break
        return self

    def hascr(self):
        return any(MonoText._re_crlf.search(s) for s in self)

    def charcategory(self):
        return ((unicodedata.category(c), c) for s in self for c in s)

    def trim(self, beginning=True, ending=True, consecutive=False):
        for i, s in enumerate(self):
            self[i] = MonoText.trimtext(s, beginning, ending, consecutive)
        return self

    def funcsearch(self, matcher):
        """
        Search segments by provided search function.
        :param matcher: function to search
        :type matcher: function
        :return: tuple of indices
        :rtype tuple of int
        """
        return (i for (i, s) in enumerate(self) if matcher(s))

    def search(self, pattern, ignorecase=False):
        return self.funcsearch(re.compile(re.escape(pattern), re.I if ignorecase else 0).search)

    def research(self, pattern, flags=0):
        return self.funcsearch(re.compile(pattern, flags).search)

    def funcreplace(self, replacer):
        indices = []
        for i, s in enumerate(self):
            newtext = replacer(s)
            if s != newtext:
                self[i] = newtext
                indices.append(i)
        return tuple(indices)

    def replace(self, pattern, repl, ignorecase=False):
        reobj = re.compile(re.escape(pattern), re.I if ignorecase else 0)
        return self.funcreplace(lambda x: reobj.sub(repl, x))

    def rereplace(self, pattern, repl, flags=0):
        reobj = re.compile(pattern, flags)
        return self.funcreplace(lambda x: reobj.sub(repl, x))

    def tokenize(self, tokenizer):
        for i, s in enumerate(self):
            self[i] = tokenizer(s)
        return self
