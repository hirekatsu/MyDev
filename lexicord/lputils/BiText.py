# -*- coding: utf-8 -*-
import sys
import codecs
import re
import os.path
import nltk
from MonoText import MonoText


class BiText(object):
    """

    """
    def __init__(self, source=(), target=()):
        self._source = MonoText(source)
        self._target = MonoText(target)

    def source(self):
        return tuple(self._source)

    def target(self):
        return tuple(self._target)

    def count(self):
        return len(self._source)

    def __iter__(self):
        class _BiTextIter(object):
            def __init__(self, bt):
                self._bt = bt
                self._i = 0

            def next(self):
                if self._i >= self._bt.count():
                    raise StopIteration()
                v = self._bt[self._i]
                self._i += 1
                return v
        return _BiTextIter(self)

    def __getitem__(self, index):
        return self._source[index], self._target[index]

    def iteritems(self):
        i = 0
        while i < len(self._source):
            yield self[i]
            i += 1

    def clone(self):
        return BiText(source=self._source, target=self._target)

    def remove(self, index):
        self._source.pop(index)
        self._target.pop(index)
        return self

    def trim(self, beginning=True, ending=True, consecutive=False):
        self._source.trim(beginning, ending, consecutive)
        self._target.trim(beginning, ending, consecutive)
        return self

    def hascr(self):
        return self._source.hascr() or self._target.hascr()

    def charcatalog(self, category=None, where='both'):
        """
        List category and occurrence frequency of each char appears in text.
        :param category: Specify unicode category to list.
        :type category: str
        :param where: 'both', 'source', or 'target'
        :type where: str
        :return: list of chars by category
        """
        assert where in ('both', 'source', 'target'), 'Invalid parameter: where.'
        ccat = []
        if where in ('both', 'source'):
            ccat += self._source.charcategory()
        if where in ('both', 'target'):
            ccat += self._target.charcategory()
        cfd = nltk.ConditionalFreqDist(ccat)
        return ((c, ', '.join(fd.keys()[0:10])+(',...' if len(fd) > 10 else ''), fd.items()) for (c, fd) in cfd.iteritems() if category is None or c == category)

    def readtext(self, sourcefilename, targetfilename, sourceencoding=sys.getdefaultencoding(),
                 targetencoding=sys.getdefaultencoding(),
                 metatextparser=None):
        self._source.readtext(sourcefilename, sourceencoding, metatextparser)
        self._target.readtext(targetfilename, targetencoding, metatextparser)
        assert(len(self._source) == len(self._target))
        return self

    def writetext(self, sourcefilename, targetfilename, sourceencoding=sys.getcheckinterval(),
                  targetencoding=sys.getcheckinterval(),
                  metatextparser=None, forcewithcr=False, start=None, end=None):
        if not forcewithcr and self.hascr():
            raise Exception('One or more segments contain carriage return, which may cause problems as corpus in '
                            'text-text formatted file')
        self._source.writetext(sourcefilename, sourceencoding, metatextparser, start, end)
        self._target.writetext(targetfilename, targetencoding, metatextparser, start, end)
        return self

    def readtmx(self, tmxfilename, encoding=sys.getdefaultencoding(),
                sourcelanguage='UNKNOWN0', targetlanguage='UNKNOWN1',
                metatextparser=None,
                progresscallback=None):
        assert os.path.exists(tmxfilename), 'TMX file does not exist.'

        if progresscallback:
            import time
            filesize = os.path.getsize(tmxfilename)
            lastcallat = time.time()

        self._source = MonoText()
        self._target = MonoText()
        with codecs.open(tmxfilename, 'r', encoding=encoding) as f:
            self._strbuf = ''
            langs = sourcelanguage
            langt = targetlanguage

            def readto(pattern, flags=0):
                for l in f:
                    self._strbuf += l
                    m = re.search(pattern, self._strbuf, flags=flags+re.U+re.S+re.M)
                    if m:
                        readtext = self._strbuf[:m.start()]
                        self._strbuf = self._strbuf[m.end():]
                        return m.group(0), readtext
                return None, self._strbuf

            if not readto(r'<body>', re.I)[0]:
                raise Exception('Unexpected EOF - no <body>')
            while readto(r'<tu(\s.*?)*>', re.I+re.U)[0]:
                (tuend, content) = readto(r'</tu>', re.I)
                if not tuend:
                    raise Exception('Unexpected EOF - no </tu>')
                tuvs = re.findall(r'(<tuv(?:\s.*?)*>)(.*?)(</tuv>)', content, re.I+re.U+re.S+re.M)
                if len(tuvs) >= 2:
                    texts = None
                    textt = None
                    if langs == 'UNKNOWN0':
                        m = re.search(r'xml:lang="(.*?)"', tuvs[0][0], re.I+re.U+re.S+re.M)
                        if m:
                            langs = m.group(1)
                    if langt == 'UNKNOWN1':
                        m = re.search(r'xml:lang="(.*?)"', tuvs[1][0], re.I+re.U+re.S+re.M)
                        if m:
                            langt = m.group(1)
                    for ix in range(0, len(tuvs)):
                        m = re.search(r'xml:lang="(.*?)"', tuvs[ix][0], re.I+re.U+re.S+re.M)
                        tuvlang = m.group(1) if m else 'UNKNOWN%s' % ix
                        if tuvlang == langs or tuvlang == langt:
                            m = re.search(r'<seg(?:\s.*?)*>(.*?)</seg>', tuvs[ix][1], re.I+re.U+re.S+re.M)
                            if m:
                                segtext = m.group(1).strip('\r\n')
                                segtext = re.sub(r'<ph(?:\s.*?)*>(.*?)</ph>', '', segtext, re.I+re.U+re.S+re.M)
                                segtext = segtext.replace(u'&apos;', u"'").replace(u'&quot;', u'"').replace(u'&lt;', u'<').replace(u'&gt;', u'>').replace(u'&amp;', u'&')
                                if metatextparser:
                                    segtext = metatextparser(segtext)
                                if tuvlang == langs:
                                    texts = segtext
                                if tuvlang == langt:
                                    textt = segtext
                    if texts is not None and textt is not None:
                        self._source.append(texts)
                        self._target.append(textt)

                if progresscallback:
                    if time.time() - lastcallat > 1.0:
                        progresscallback(float(f.tell()) / filesize)
                        lastcallat = time.time()
        return self

    def _map(self, func, limit=0):
        indices = []
        for i, (s, t) in enumerate(self.iteritems()):
            if func(i, s, t):
                indices.append(i)
                if limit > 0 and len(indices) >= limit:
                    break
        return indices

    def _search(self, pattern, where='any', ignorecase=False, regex=False, regexflags=0, limit=0):
        if hasattr(pattern, '__call__'):
            evaluator = pattern
        else:
            assert isinstance(pattern, basestring), 'Pattern is not string.'
            if regex:
                reobj = re.compile(pattern, regexflags)
            else:
                reobj = re.compile(re.escape(pattern), re.I if ignorecase else 0)
            evaluator = reobj.search
        sourcefunc = evaluator if where in ('source', 'both', 'any') else lambda x: False
        targetfunc = evaluator if where in ('target', 'both', 'any') else lambda x: False
        if where == 'both':
            func = lambda i, s, t: sourcefunc(s) and targetfunc(t)
        else:
            func = lambda i, s, t: sourcefunc(s) or targetfunc(t)
        return self._map(func, limit=limit)

    def search(self, pattern, where='any', ignorecase=False, regex=False, regexflags=0, limit=0):
        return (self[i] for i in self._search(pattern, where, ignorecase, regex, regexflags, limit))

    def prune(self, pattern, where='any', ignorecase=False, regex=False, regexflags=0):
        indices = self._search(pattern, where, ignorecase, regex, regexflags)
        pruned = []
        for i in indices:
            pruned.append(self[i])
        for i in sorted(indices, reverse=True):
            self.remove(i)
        return tuple(pruned)

    def replace(self, pattern, repl='', where='any', ignorecase=False, regex=False, regexflags=0):
        if hasattr(pattern, '__call__'):
            replacer = pattern
        else:
            assert isinstance(pattern, basestring), 'Pattern is not string.'
            if regex:
                reobj = re.compile(pattern, regexflags)
            else:
                reobj = re.compile(re.escape(pattern), re.I if ignorecase else 0)
            replacer = lambda x: reobj.sub(repl, x)
        sourcefunc = replacer if where in ('source', 'any') else lambda x: x
        targetfunc = replacer if where in ('target', 'any') else lambda x: x

        def func(i, s, t):
            newsource = sourcefunc(s)
            newtarget = targetfunc(t)
            if newsource == s and newtarget == t:
                return False
            self._source[i] = newsource
            self._target[i] = newtarget
            return True
        return len(self._map(func))

    def duplicate(self, where='both', ignorecase=False, strip=False, uniq=False):
        assert where in ('both', 'source', 'target'), 'Invalid parameter: where.'
        if ignorecase:
            if strip:
                prep = lambda x: MonoText.trimtext(x.lower(), True, True, True)
            else:
                prep = lambda x: x.lower()
        else:
            if strip:
                prep = lambda x: MonoText.trimtext(x, True, True, True)
            else:
                prep = lambda x: x
        if where == 'both':
            keygenerator = lambda s, t: u'\\u0000'.join([prep(s), prep(t)])
        elif where == 'source':
            keygenerator = lambda s, t: prep(s)
        else:
            keygenerator = lambda s, t: prep(t)
        dupsdict = {}

        def func(i, s, t):
            key = keygenerator(s, t)
            if key in dupsdict:
                dupsdict[key].append(i)
            else:
                dupsdict[key] = [i]
            return False
        self._map(func)
        dupslist = [v for v in dupsdict.itervalues() if len(v) > 1]

        # duplicates = (nltk.FreqDist(self[i] for i in indices).items() for indices in dupslist)
        # if the option uniq = True is specified, the comprehension might not work because the element has
        # already been removed when the element is referred.
        duplicates = []
        for indices in dupslist:
            duplicates.append(nltk.FreqDist(self[i] for i in indices).items())
        if uniq:
            for i in sorted((v for indices in dupslist for v in indices[1:]), reverse=True):
                self.remove(i)
        return tuple(duplicates)

    def empty(self, where='any', strip=False, prune=False):
        assert where in ('any', 'both', 'source', 'target'), 'Invalid parameter: where.'
        if strip:
            prep = lambda x: MonoText.trimtext(x, True, True, True)
        else:
            prep = lambda x: x
        if where != 'target':
            sourceisempty = lambda x: len(prep(x)) == 0
        else:
            sourceisempty = lambda x: False
        if where != 'source':
            targetisempty = lambda x: len(prep(x)) == 0
        else:
            targetisempty = lambda x: False
        if where == 'both':
            func = lambda i, s, t: sourceisempty(s) and targetisempty(t)
        else:
            func = lambda i, s, t: sourceisempty(s) or targetisempty(t)
        indices = self._map(func)

        empties = []
        for i in indices:
            empties.append(self[i])
        if prune:
            for i in sorted(indices, reverse=True):
                self.remove(i)
        return tuple(empties)

    def tokenize(self, sourcetokenizer, targettokenizer):
        self._source.tokenize(sourcetokenizer)
        self._target.tokenize(targettokenizer)
        return self

    _re_moses = [
        (re.compile(r'[\x00-\x1F]'), ''),
        (re.compile(r'\s+'), ' '),
        (re.compile(r'&'), '&amp;'),
        (re.compile(r'\|'), '&#124;'),
        (re.compile(r'<'), '&lt;'),
        (re.compile(r'>'), '&gt;'),
        (re.compile(r"'"), '&apos;'),
        (re.compile(r'"'), '&quot;'),
        (re.compile(r'\['), '&#91;'),
        (re.compile(r'\]'), '&#93;')
    ]
    @staticmethod
    def escape_moses_special_char(text):
        for p, s in BiText._re_moses:
            text = p.sub(s, text)
        return text


class BiTextPrint():
    def __init__(self, bt):
        self._bt = bt
        self._pbuf = ''

    def readtmx(self, tmxfilename, encoding=sys.getdefaultencoding(),
                sourcelanguage='UNKNOWN0', targetlanguage='UNKNOWN1',
                metatextparser=None):
        def myprogress(x):
            print '\r{0}% '.format(int(x * 100)), '*' * int(x * 25),
        self._bt.readtmx(tmxfilename, encoding, sourcelanguage, targetlanguage, metatextparser,
                         rogresscallback=myprogress)
        print '\r'
        return self

    def charcatalog(self, category=None, where='both', details=False):
        result = self._bt.charcatalog(category, where)
        for c, s, l in result:
            self._myprint(u'"{0}" : {1}'.format(c, s))
            if details:
                for v, o in sorted(l, key=lambda v: ord(v[0])):
                    self._myprint(u'    {0} (\\u{1:0>4X}) : {2}'.format(v, ord(v), o))
            self._myprint(u'{0} item(s).'.format(len(l)))
        return self._myflush()

    def search(self, pattern, where='any', ignorecase=False, regex=False, regexflags=0, limit=0):
        result = self._bt.search(pattern, where, ignorecase, regex, regexflags, limit)
        count = 0
        for s, t in result:
            self._myprint('-' * 40, u'source: {0}'.format(s), u'target: {0}'.format(t))
            count += 1
        self._myprint('-' * 40)
        if count == 0:
            self._myprint('*** NO MATCH ***')
        else:
            self._myprint('{0} item(s) found.'.format(count))
        return self._myflush()

    def prune(self, pattern, where='any', ignorecase=False, regex=False, regexflags=0):
        result = self._bt.prune(pattern, where, ignorecase, regex, regexflags)
        count = 0
        for s, t in result:
            self._myprint('-' * 40, u'source: {0}'.format(s), u'target: {0}'.format(t))
            count += 1
        self._myprint('-' * 40)
        self._myprint('{0} item(s) pruned.'.format(count))
        return self._myflush()

    def duplicate(self, where='both', ignorecase=False, strip=False, uniq=False):
        result = self._bt.duplicate(where, ignorecase, strip, uniq)
        for v in result:
            self._myprint('=' * 40)
            for (s, t), o in v:
                self._myprint(u'source: {0}\ntarget: {1}\noccurrence: {2}'.format(s, t, o))
        return self._myflush()

    def empty(self, where='any', strip=False, prune=False):
        result = self._bt.empty(where, strip, prune)
        for s, t in result:
            self._myprint("-" * 40)
            self._myprint(u'source: {0}\ntarget: {1}'.format(s, t))
        return self._myflush()

    def printcode(self, text):
        for c in text:
            print '{0} ({1:0>4X}) '.format(c, ord(c)),
        print ''

    def _myprint(self, *args):
        for m in args:
            print m
            self._pbuf += m + u'\n'

    def _myflush(self):
        r = self._pbuf
        self._pbuf = ''
        return r


if __name__ == '__main__':
    bt = BiText()
    bp = BiTextPrint(bt)
    bp.readtmx(r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/vasont.tmx', encoding='utf-8')
    # print bp.source()[0:30]
    # for s in bp[100]:
    #     print s
    bt.trim(True, True, True)
    print bt.count()
    # for i, v in enumerate(bp.concordance(u'Symantec', where='both', limit=10)):
    #     print i, ':'
    #     print v[0]
    #     print v[1]
    # print '-' * 20, 'duplicate', '-' * 20
    # a = bp.duplicate(where='both', ignorecase=False, strip=False, uniq=True)
    # print bp.count()
    print '-' * 20, 'empty', '-' * 20
    a = bp.empty(where='any', strip=True, prune=False)
    print bt.count()
    # print '-' * 20, 'prune', '-' * 20
    # print '-' * 20, 'concordance', '-' * 20
    # for s, t in bc.concordance(u'\u2666', where='both'):
    #     print u'source: {0}\ntarget: {1}\n----------'.format(s, t)
    # print '-' * 20, 'replace', '-' * 20
    # bc.replace(u'<\u2666\u2666\u2666>', '', where='both')
    # print '-' * 20, 'concordance(2)', '-' * 20
    # for s, t in bc.concordance(u'\u2666', where='both'):
    #     print u'source: {0}\ntarget: {1}\n----------'.format(s, t)
    # print '-' * 20, 'charcatalog', '-' * 20
    # for c, s, d in bc.charcatalog():
    #     print u'"{0}": {1}'.format(c, s)
    #     for v, o in d:
    #         print u'    {0}  (\\u{1:0>4X}) : {2}'.format(v, ord(v), o)

    import MeCab
    mt = MeCab.Tagger('-Owakati -u /Users/kiyoshi_izumi/Desktop/DATA/DEV/MyGitHub/MyDev/lexicord/mydic.dic')

    tokens = []
    for i, (_, t) in enumerate(bt):
        try:
            v = t.encode('utf8')
        except Exception as e:
            continue
        x = mt.parse(v)
        tokens += x.split()
    l = sorted(set(tokens), key=lambda x: len(x), reverse=True)
    for t in l[0:100]:
        print t
