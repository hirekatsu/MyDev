# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os.path
import re
import time
import codecs
import unicodedata
import HTMLParser
import nltk
from lputils.mosestruecase import MosesTruecaser
from lputils.unicodeprint import unicodeprint as uprint


class SegList(list):
    """
    A subclass of Python list for monolingual text.
    """
    _re_crlf = re.compile(r'[\r\n]', re.M)

    @staticmethod
    def find_crlf(text):
        return SegList._re_crlf.search(text) is not None

    @staticmethod
    def _re_subs(text, regexps):
        for p, r in regexps:
            text = p.sub(r, text)
        return text

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
    def moses_escape_text(text):
        return SegList._re_subs(text, SegList._re_moses)

    _re_trim = [
        (re.compile(r'\s+'), ' '),
        (re.compile(r'^ | $'), '')
    ]

    @staticmethod
    def trim_text(text):
        return SegList._re_subs(text, SegList._re_trim)

    def __init__(self, seq=()):
        super(SegList, self).__init__(seq)

    def __getslice__(self, i, j):
        return SegList(list.__getslice__(self, i, j))

    def __add__(self, other):
        return SegList(list.__add__(self, other))

    def __mul__(self, other):
        return SegList(list.__mul__(self, other))

    def __getitem__(self, item):
        element = list.__getitem__(self, item)
        if isinstance(item, slice):
            element = SegList(element)
        return element

    def has_crlf(self):
        return any(SegList.find_crlf(s) for s in self)

    def _find(self, matcher, limit=0):
        res = []
        for i, s in enumerate(self):
            if matcher(s):
                res.append((i, s))
                if 0 < limit <= len(res):
                    break
        return res

    def _do(self, func):
        res = []
        for i, s in enumerate(self):
            newS = func(s)
            if s != newS:
                self[i] = newS
                res.append((i, newS))
        return res

    def trim(self):
        return [s for (_, s) in self._do(SegList.trim_text)]

    def lower(self):
        return [s for (_, s) in self._do(lambda x: x.lower())]

    def tokenize(self, tokenizer):
        return [s for (_, s) in self._do(tokenizer)]

    def moses_escape(self):
        return self._do(SegList.moses_escape_text)

    def moses_truecase(self, possibly_use_first_token=False):
        pass

    def research(self, pattern, flags=0, limit=0):
        regex = re.compile(pattern, flags)
        return [s for (_, s) in self._find(lambda x: regex.search(x), limit=limit)]

    def search(self, pattern, ignorecase=False, limit=0):
        return self.research(re.escape(pattern), flags=(re.I if ignorecase else 0), limit=limit)

    def rereplace(self, pattern, repl, flags=0):
        regex = re.compile(pattern, flags)
        return [s for (_, s) in self._do(lambda x: regex.sub(repl, x))]

    def replace(self, pattern, repl, ignorecase=False):
        return self.rereplace(re.escape(pattern), repl, flags=(re.I if ignorecase else 0))

    def read(self, name, encoding=sys.getdefaultencoding(), metatextparser=None):
        assert os.path.exists(name), 'File does not exist.'
        if not metatextparser:
            metatextparser = lambda x: x
        with codecs.open(name, encoding=encoding) as f:
            self.extend(metatextparser(l.strip()) for l in f)
        return self

    def write(self, name, encoding=sys.getdefaultencoding(), metatextparser=None, assert_crlf=True):
        if assert_crlf and self.has_crlf():
            raise Exception('One or more segments contain carriage return, which may cause problems as corpus in '
                            'plain-text formatted file')
        if not metatextparser:
            metatextparser = lambda x: x
        with codecs.open(name, 'w', encoding=encoding) as f:
            for s in self:
                f.write(metatextparser(s) + '\n')
        return self


class _Xreader(object):
    def __init__(self, name, element, flags=0):
        self._name = name
        self._begin = re.compile(ur'<%s(\s[^>]*)?>' % re.escape(element), flags=flags+re.U+re.S+re.M)
        self._end = re.compile(ur'</%s>' % re.escape(element), flags=flags+re.U+re.S+re.M)
        self._buffer = u''

    def iter(self):
        _, begin = self._read_to(self._begin)
        while begin:
            content, end = self._read_to(self._end)
            if end is None:
                raise Exception('Unexpected EOF --- closing %s not found' % self._end.pattern)
            yield begin, content, end
            _, begin = self._read_to(self._begin)

    def _read_to(self, reobj):
        while True:
            m = reobj.search(self._buffer)
            if m:
                before = self._buffer[:m.start()]
                found = m.group(0)
                self._buffer = self._buffer[m.end():]
                return before, found
            line = self._name.next()
            if not line:
                break
            self._buffer += line
        return None, None


class BiSegList(list):
    """
    A subclass of Python list for bilingual text.
    Each element consists of a tuple containing two unicode strings (source and target).
    """

    @staticmethod
    def helper_format_catalog(catalog):
        from lputils.unicodeprint import unicodeprint
        for category in catalog:
            if isinstance(category, basestring):
                unicodeprint.pprint(category)
            else:
                name, freq = category
                unicodeprint.pprint(name)
                for (c, f) in sorted(freq, key=lambda x: ord(x[0])):
                    unicodeprint.pprint(u'  {0} ({1:0>4x}): {2}'.format(c, ord(c), f))

    def __init__(self, seq=()):
        super(BiSegList, self).__init__(seq)

    def __getslice__(self, i, j):
        return BiSegList(list.__getslice__(self, i, j))

    def __add__(self, other):
        return BiSegList(list.__add__(self, other))

    def __mul__(self, other):
        return BiSegList(list.__mul__(self, other))

    def __getitem__(self, item):
        element = list.__getitem__(self, item)
        if isinstance(item, slice):
            element = BiSegList(element)
        return element

    @staticmethod
    def _htmlencode(t):
        return t.replace(u'&', u'&amp;').replace(u"'", u'&apos;').replace(u'"', u'&quot;').replace(u'<', u'&lt;').replace(u'>', u'&gt;')

    @staticmethod
    def _wh(key, target):
        return key in (target, 'both', 'any')

    def has_crlf(self):
        return any((SegList.find_crlf(s) or SegList.find_crlf(t)) for (s, t) in self)

    def charcat(self, where='both', categories=None, detail=False):
        charcat = []
        if self._wh(where, 'source'):
            charcat += [(unicodedata.category(c), c) for (s, _) in self for c in s]
        if self._wh(where, 'target'):
            charcat += [(unicodedata.category(c), c) for (_, t) in self for c in t]
        cfd = nltk.ConditionalFreqDist(charcat)
        catalog = sorted(filter(lambda x: not categories or x[0] == categories or x[0] in categories,
                                cfd.iteritems()),
                         key=lambda x: x[0])
        if not detail:
            catalog = [cat + u': ' + u' '.join(u'{0} ({1:0>4x})'.format(c, ord(c)) for c in fd.keys()[:10]) + (' ...' if len(fd.keys()) > 10 else '') for (cat, fd) in catalog]
        else:
            catalog = [(cat, [(c, f) for (c, f) in sorted(fd.iteritems(), key=lambda i: i[0])]) for (cat, fd) in catalog]
        return catalog

    def _find(self, matcher, limit=0):
        res = []
        for i, (s, t) in enumerate(self):
            if matcher(s, t):
                res.append(i)
                if 0 < limit <= len(res):
                    break
        return res

    def _do(self, func):
        res = []
        for i, (s, t) in enumerate(self):
            newS, newT = func(s, t)
            if s != newS or t != newT:
                self[i] = (newS, newT)
                res.append(i)
        return res

    def _extract(self, indices):
        return [self[i] for i in indices]

    def trim(self, where='both'):
        funcS = SegList.trim_text if self._wh(where, 'source') else (lambda x: x)
        funcT = SegList.trim_text if self._wh(where, 'target') else (lambda x: x)
        return self._do(lambda s, t: (funcS(s), funcT(t)))

    def lower(self):
        return self._do(lambda s, t: (s.lower(), t.lower()))

    def tokenize(self, sourcetokenizer=None, targettokenizer=None):
        if not sourcetokenizer:
            sourcetokenizer = lambda x: x
        if not targettokenizer:
            targettokenizer = lambda x: x
        return self._do(lambda s, t: (sourcetokenizer(s), targettokenizer(t)))

    def cutoff(self, min=1, max=80, ratio=0):
        def evaluate(s, t):
            sc, tc = len(s.split()), len(t.split())
            if sc < min or tc < min or sc > max or tc > max:
                return True
            if ratio > 0 and (float(sc)/tc > ratio or float(tc)/sc > ratio):
                return True
            return False
        indices = self._find(evaluate)
        pruned = self._extract(indices)
        self.prune(indices)
        return pruned

    def moses_escape(self):
        return self._do(lambda s, t: (SegList.moses_escape_text(s), SegList.moses_escape_text(t)))

    def moses_truecase(self, where='both', possibly_use_first_token=False,
                       source_model_name=None, target_model_name=None):
        if self._wh(where, 'source'):
            truecaser = MosesTruecaser().train((s for (s, t) in self), possibly_use_first_token=possibly_use_first_token)
            if source_model_name:
                truecaser.write(source_model_name)
            self._do(lambda s, t: (truecaser.truecase(s), t))
        if self._wh(where, 'target'):
            truecaser = MosesTruecaser().train((t for (s, t) in self), possibly_use_first_token=possibly_use_first_token)
            if target_model_name:
                truecaser.write(target_model_name)
            self._do(lambda s, t: (s, truecaser.truecase(t)))
        return self

    def prune(self, indices):
        for i in sorted(indices, reverse=True):
            self.pop(i)
        return self

    def _search(self, pattern, where='any', flags=0, limit=0):
        regex = re.compile(pattern, flags)
        funcS = (lambda x: regex.search(x)) if self._wh(where, 'source') else (lambda x: False)
        funcT = (lambda x: regex.search(x)) if self._wh(where, 'target') else (lambda x: False)
        func = (lambda x, y: funcS(x) and funcT(y)) if where == 'both' else (lambda x, y: funcS(x) or funcT(y))
        return self._find(func, limit=limit)

    def research(self, pattern, where='any', flags=0, limit=0):
        return self._search(pattern, where=where, flags=flags, limit=limit)

    def search(self, pattern, where='any', ignorecase=False, limit=0):
        return self._search(re.escape(pattern), where=where, flags=(re.I if ignorecase else 0), limit=limit)

    def rereplace(self, pattern, repl, where='both', flags=0):
        regex = re.compile(pattern, flags)
        funcS = (lambda x: regex.sub(repl, x)) if self._wh(where, 'source') else (lambda x: x)
        funcT = (lambda x: regex.sub(repl, x)) if self._wh(where, 'target') else (lambda x: x)
        return self._do(lambda s, t: (funcS(s), funcT(t)))

    def replace(self, pattern, repl, where='both', ignorecase=False):
        return self.rereplace(re.escape(pattern), repl, where=where, flags=(re.I if ignorecase else 0))

    def empty(self, where='any'):
        funcS = (lambda x: len(x) == 0) if self._wh(where, 'source') else (lambda x: False)
        funcT = (lambda x: len(x) == 0) if self._wh(where, 'target') else (lambda x: False)
        func = (lambda s, t: funcS(s) and funcT(t)) if where == 'both' else (lambda s, t: funcS(s) or funcT(t))
        return self._find(func)

    def identical(self, ignorecase=False):
        prep = (lambda x: x.lower()) if ignorecase else (lambda x: x)
        func = lambda s, t: prep(s) == prep(t)
        return self._find(func)

    def duplicate(self, where='both'):
        assert where in ('both', 'source', 'target'), 'Invalid parameter: where.'
        if where == 'both':
            keygenerate = lambda s, t: s + u'\u0000' + t
        elif where == 'source':
            keygenerate = lambda s, t: s
        else:
            keygenerate = lambda s, t: t
        freq = {}
        for i, (s, t) in enumerate(self):
            key = keygenerate(s, t)
            if key in freq:
                freq[key].append(i)
            else:
                freq[key] = [i]
        return [group for group in freq.itervalues() if len(group) > 1]

    def duprune(self, indices):
        return self.prune(sorted((i for group in indices for i in group[1:]), reverse=True))

    def pprint(self, indices):
        if indices and hasattr(indices, '__iter__'):
            if isinstance(indices[0], int):
                for i in indices:
                    print('{}:'.format(i))
                    print(self[i][0])
                    print(self[i][1])
            else:
                print('-' * 40)
                for group in indices:
                    self.pprint(group)
                    print('-' * 40)

    def read(self, format, name, encoding=sys.getdefaultencoding(), **kwargs):
        if format == 'text':
            assert not isinstance(name, basestring), 'Parameter: name is NOT a list'
            assert hasattr(name, '__iter__'), 'Parameter: name is NOT an iterable'
            assert len(name) == 2, 'Length of parameter: name is NOT two'
            assert all(isinstance(n, basestring) for n in name), 'One or more elements in parameter: name are NOT string'
            if isinstance(encoding, basestring):
                encoding = (encoding, encoding)
            return self._read_text(sourcename=name[0], targetname=name[1],
                                   sourceencoding=encoding[0], targetencoding=encoding[1], **kwargs)
        elif format == 'tabbed':
            assert isinstance(name, basestring), 'Parameter: name is NOT a string'
            return self._read_tabbed(name, encoding=encoding, **kwargs)
        elif format == 'tmx':
            assert isinstance(name, basestring), 'Parameter: name is NOT a string'
            return self._read_tmx(name, encoding=encoding, **kwargs)
        elif format == 'xliff':
            assert isinstance(name, basestring), 'Parameter: name is NOT a string'
            return self._read_xliff(name, encoding=encoding, **kwargs)
        else:
            raise Exception('Unknown file format: ' + format)

    def write(self, format, name, encoding=sys.getdefaultencoding(), **kwargs):
        if format == 'text':
            assert not isinstance(name, basestring), 'Parameter: name is NOT a list'
            assert hasattr(name, '__iter__'), 'Parameter: name is NOT an iterable'
            assert len(name) == 2, 'Length of parameter: name is NOT two'
            assert all(isinstance(n, basestring) for n in name), 'One or more elements in parameter: name are NOT string'
            if isinstance(encoding, basestring):
                encoding = (encoding, encoding)
            return self._write_text(sourcename=name[0], targetname=name[1],
                                    sourceencoding=encoding[0], targetencoding=encoding[1], **kwargs)
        elif format == 'tabbed':
            assert isinstance(name, basestring), 'Parameter: name is NOT a string'
            return self._write_tabbed(name, encoding=encoding, **kwargs)
        elif format == 'tmx':
            assert isinstance(name, basestring), 'Parameter: name is NOT a string'
            return self._write_tmx(name, encoding=encoding, **kwargs)
        elif format == 'xliff':
            assert isinstance(name, basestring), 'Parameter: name is NOT a string'
            return self._write_xliff(name, encoding=encoding, **kwargs)
        else:
            raise Exception('Unknown file format: ' + format)

    def _read_text(self, sourcename, targetname,
                   sourceencoding=sys.getdefaultencoding(), targetencoding=sys.getdefaultencoding(),
                   metatextparser=None):
        assert os.path.exists(sourcename), 'Source file does not exist.'
        assert os.path.exists(targetname), 'Target file does not exist.'
        if not metatextparser:
            metatextparser = lambda x: x
        with codecs.open(sourcename, encoding=sourceencoding) as fS:
            with codecs.open(targetname, encoding=targetencoding) as fT:
                self.extend(zip((metatextparser(lS.strip()) for lS in fS), (metatextparser(lT.strip()) for lT in fT)))
        return self

    def _write_text(self, sourcename, targetname,
                    sourceencoding=sys.getdefaultencoding(), targetencoding=sys.getdefaultencoding(),
                    metatextparser=None,
                    assert_crlf=True):
        if assert_crlf and self.has_crlf():
            raise Exception('One or more segments contain carriage return, which may cause problems as corpus in '
                            'plain-text formatted file')
        if not metatextparser:
            metatextparser = lambda x: x
        with codecs.open(sourcename, 'w', encoding=sourceencoding) as fS:
            with codecs.open(targetname, 'w', encoding=targetencoding) as fT:
                for s, t in self:
                    fS.write(metatextparser(s) + u'\n')
                    fT.write(metatextparser(t) + u'\n')
        return self

    def _read_tabbed(self, name, encoding=sys.getdefaultencoding(), metatextparser=None):
        assert os.path.exists(name), 'File does not exist.'
        if not metatextparser:
            metatextparser = lambda x: x
        with codecs.open(name, encoding=encoding) as f:
            for l in f:
                x = l.strip().split(u'\t')
                self.append((metatextparser(x[0]), metatextparser(x[1] if len(x) > 1 else u'')))
        return self

    def _write_tabbed(self, name, encoding=sys.getdefaultencoding(), metatextparser=None):
        if not metatextparser:
            metatextparser = lambda x: x
        with codecs.open(name, 'w', encoding=encoding) as f:
            for s, t in self:
                f.write(metatextparser(s) + u'\t' + metatextparser(t) + u'\n')

    def _read_tmx(self, name, lang=(u'<UNKNOWN0>', u'<UNKNOWN1>'), encoding=sys.getdefaultencoding(),
                  metatextparser=None,
                  progresscallback=None,
                  verbose=False):
        """
        (Private method) Read segment text from a TMX file and append the current segment list.
        :param name: Filename
        :param lang:
        :param encoding:
        :param metatextparser:
        :param progresscallback:
        :param verbose:
        :return:
        """
        assert os.path.exists(name), 'TMX file does not exist.'

        filesize = os.path.getsize(name)
        lastprogressat = time.time()

        with codecs.open(name, 'r', encoding=encoding) as f:
            htmlparser = HTMLParser.HTMLParser()
            reader = _Xreader(f, u'tu')
            langS, langT = lang
            for stag, TU, etag in reader.iter():
                TUVs = re.findall(ur'(<tuv(?:\s[^>]*)?>)(.*?)(</tuv>)', TU, re.I + re.U + re.S + re.M)
                if len(TUVs) >= 2:
                    textS, textT = None, None
                    if langS == u'<UNKNOWN0>':
                        m = re.search(ur'xml:lang="(.*?)"', TUVs[0][0], re.I + re.U + re.S + re.M)
                        if m:
                            langS = m.group(1)
                    if langT == u'<UNKNOWN1>':
                        m = re.search(ur'xml:lang="(.*?)"', TUVs[1][0], re.I + re.U + re.S + re.M)
                        if m:
                            langT = m.group(1)
                    for ix, TUV in enumerate(TUVs):
                        m = re.search(ur'xml:lang="(.*?)"', TUV[0], re.I + re.U + re.S + re.M)
                        lang = m.group(1) if m else u'<UNKNOWN%s>' % ix
                        if lang == langS or lang == langT:
                            m = re.search(ur'<seg(?:\s[^>]*)?>(.*?)</seg>', TUV[1], re.I + re.U + re.S + re.M)
                            if m:
                                text = m.group(1).strip(u'\r\n')
                                text = re.sub(ur'<ph(?:\s[^>]*)?>(.*?)</ph>', ur'\1', text, re.I + re.U + re.S + re.M)
                                text = re.sub(ur'<ut>(.*)</ut>', ur'\1', text, re.I + re.U + re.S + re.M)
                                text = htmlparser.unescape(text)
                                if metatextparser:
                                    text = metatextparser(text)
                                if lang == langS:
                                    textS = text
                                if lang == langT:
                                    textT = text
                    if textS is not None and textT is not None:
                        self.append((textS, textT))
                if time.time() - lastprogressat > 1.0:
                    rate = float(f.tell()) / filesize
                    if verbose:
                        print('\r{:>3d}%'.format(int(rate * 100)), '*' * int(rate * 20), end=' ')
                    if progresscallback:
                        progresscallback(rate)
                    lastprogressat = time.time()
        if verbose:
            print('\r100%', '*' * 20)
        return self

    def _write_tmx(self, name, lang, encoding=sys.getdefaultencoding(),
                   metatextparser=None,
                   progresscallback=None,
                   verbose=False):
        from datetime import datetime
        from pytz import timezone

        if metatextparser is None:
            metatextparser = lambda x: x

        lastprogressat = time.time()

        with codecs.open(name, 'w', encoding=encoding) as f:
            f.write(u'''<?xml version="1.0" encoding="{}"?>
<tmx version="1.4">
<header creationtool="py script" creationtoolversion="1.0" segtype="sentence" adminlang="EN" srclang="{}" datatype="" o-encoding="" creationdate="{}Z"></header>
<body>
'''.format(encoding, lang[0], datetime.now(timezone('UTC')).strftime(u'%Y%m%dT%H%M%S')))

            for i, (s, t) in enumerate(self):
                f.write(u'''<tu>
<tuv xml:lang="{}">
<seg>{}</seg>
</tuv>
'''.format(lang[0], self._htmlencode(metatextparser(s))))
                f.write(u'''<tuv xml:lang="{}">
<seg>{}</seg>
</tuv>
</tu>
'''.format(lang[1], self._htmlencode(metatextparser(t))))
                if time.time() - lastprogressat > 1.0:
                    rate = float(i) / len(self)
                    if verbose:
                        print('\r{:>3d}%'.format(int(rate * 100)), '*' * int(rate * 20), end=' ')
                    if progresscallback:
                        progresscallback(rate)
                    lastprogressat = time.time()
            f.write(u'''</body>
</tmx>
''')
        if verbose:
            print('\r100%', '*' * 20)
        return self

    def _read_xliff(self, name, encoding=sys.getdefaultencoding(), metatextparser=None):
        assert os.path.exists(name), 'XLIFF file does not exist.'
        with codecs.open(name, 'r', encoding=encoding) as f:
            htmlparser = HTMLParser.HTMLParser()
            reader = _Xreader(f, u'xlf:trans-unit')
            for stag, TU, etag in reader.iter():
                if re.search(ur'translate="no"', stag):
                    continue
                su = re.search(ur'<xlf:source(?:\s[^>]*)?>(.*?)</xlf:source>', TU, re.I + re.U + re.S + re.M)
                tu = re.search(ur'<xlf:target(?:\s[^>]*)?>(.*?)</xlf:target>', TU, re.I + re.U + re.S + re.M)
                if su and tu:
                    stext = su.group(1).strip(u'\r\n')
                    stext = re.sub(ur'<ph(?:\s[^>]*)?>(.*?)</ph>', ur'\1', stext, re.I + re.U + re.S + re.M)
                    stext = htmlparser.unescape(stext)
                    if metatextparser:
                        stext = metatextparser(stext)
                    ttext = tu.group(1).strip(u'\r\n')
                    ttext = re.sub(ur'<ph(?:\s[^>]*)?>(.*?)</ph>', ur'\1', ttext, re.I + re.U + re.S + re.M)
                    ttext = htmlparser.unescape(ttext)
                    if metatextparser:
                        ttext = metatextparser(ttext)
                    self.append((stext, ttext))
        return self

    def _write_xliff(self, name, lang, encoding=sys.getdefaultencoding(),
                     originalname='translate.txt', originaldatatype='plaintext',
                     metatextparser=None):
        if metatextparser is None:
            metatextparser = lambda x: x
        with codecs.open(name, 'w', encoding=encoding) as f:
            f.write(u'''<?xml version="1.0" encoding="utf-8"?>
<xlf:xliff xmlns:xlf="urn:oasis:names:tc:xliff:document:1.2" version="1.2">
<xlf:file datatype="{}" original="{}" source-language="{}" target-language="{}">
<xlf:body>
'''.format(originaldatatype, originalname, lang[0], lang[1]))
            for i, (s, t) in enumerate(self):
                f.write(u'''<xlf:trans-unit id="{}">
<xlf:source>{}</xlf:source>
<xlf:target>{}</xlf:target>
</xlf:trans-unit>
'''.format(i, self._htmlencode(metatextparser(s)), self._htmlencode(metatextparser(t))))
            f.write(u'''</xlf:body>
</xlf:file>
</xlf:xliff>
''')

if __name__ == '__main__':
    from local_settings import myenv
    bslist = BiSegList()
    bslist.read(format='tmx', name=myenv.tmxV, encoding='utf-8', verbose=True)
    print(len(bslist))
    subset = bslist[100:110]
    print(type(subset))
    print(len(subset))
    uprint.pprint(subset)
    BiSegList.helper_format_catalog(bslist.charcat())
    bslist.pprint(bslist.research(u'カンマ区切り'))
    bslist.rereplace(r'{\d+}', '')
    uprint.pprint(len(bslist.trim()))
    uprint.pprint(len(bslist.prune(bslist.empty())))
    bslist.pprint(bslist.research(u'^$'))
    uprint.pprint(len(bslist))
    # bslist.pprint(bslist.duplicate())
    uprint.pprint(len(bslist.duprune(bslist.duplicate())))
    uprint.pprint(len(bslist))
    uprint.pprint(bslist.cutoff())
    uprint.pprint(len(bslist))
    print('tokenizing...')
    bslist.tokenize(sourcetokenizer=lambda x: ' '.join(nltk.word_tokenize(x)), targettokenizer=None)
    bslist.moses_escape()
    print('truecasing...')
    bslist.moses_truecase(where='source')
