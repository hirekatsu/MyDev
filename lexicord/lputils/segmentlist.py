# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import os.path
import re
import time
import codecs
import unicodedata
import nltk
from lputils.mosestruecase import MosesTruecaser


class SegmentList(list):
    """
    A subclass of Python list for monolingual text.
    """
    _re_crlf = re.compile(r'[\r\n]', re.M)

    @staticmethod
    def find_crlf(text):
        return SegmentList._re_crlf.search(text) is not None

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
        return SegmentList._re_subs(text, SegmentList._re_moses)

    _re_trim = [
        (re.compile(r'\s+'), ' '),
        (re.compile(r'^ | $'), '')
    ]

    @staticmethod
    def trim_text(text):
        return SegmentList._re_subs(text, SegmentList._re_trim)

    def __init__(self, seq=()):
        super(SegmentList, self).__init__(seq)

    def __getslice__(self, i, j):
        return SegmentList(list.__getslice__(self, i, j))

    def __add__(self, other):
        return SegmentList(list.__add__(self, other))

    def __mul__(self, other):
        return SegmentList(list.__mul__(self, other))

    def __getitem__(self, item):
        element = list.__getitem__(self, item)
        if isinstance(item, slice):
            element = SegmentList(element)
        return element

    def hasCRLF(self):
        return any(SegmentList.find_crlf(s) for s in self)

    def _dofind(self, matcher, limit=0):
        res = []
        for i, s in enumerate(self):
            if matcher(s):
                res.append((i, s))
                if 0 < limit <= len(res):
                    break
        return res

    def _doeach(self, func):
        res = []
        for i, s in enumerate(self):
            newS = func(s)
            if s != newS:
                self[i] = newS
                res.append((i, newS))
        return res

    def trim(self):
        return [s for (_, s) in self._doeach(SegmentList.trim_text)]

    def lower(self):
        return [s for (_, s) in self._doeach(lambda x: x.lower())]

    def tokenize(self, tokenizer):
        return [s for (_, s) in self._doeach(tokenizer)]

    def moses_escape(self):
        return self._doeach(SegmentList.moses_escape_text)

    def moses_truecase(self, possiblyUseFirstToken=False):
        pass

    def search_re(self, pattern, flags=0, limit=0):
        regex = re.compile(pattern, flags)
        return [s for (_, s) in self._dofind(lambda x: regex.search(x), limit=limit)]

    def search(self, pattern, ignorecase=False, limit=0):
        return self.search_re(re.escape(pattern), flags=(re.I if ignorecase else 0), limit=limit)

    def replace_re(self, pattern, repl, flags=0):
        regex = re.compile(pattern, flags)
        return [s for (_, s) in self._doeach(lambda x: regex.sub(repl, x))]

    def replace(self, pattern, repl, ignorecase=False):
        return self.replace_re(re.escape(pattern), repl, flags=(re.I if ignorecase else 0))

    def read(self, name, encoding=sys.getdefaultencoding(), metatextparser=None):
        assert os.path.exists(name), 'File does not exist.'
        if not metatextparser:
            metatextparser = lambda x: x
        with codecs.open(name, encoding=encoding) as f:
            self.extend(metatextparser(l.strip()) for l in f)
        return self

    def write(self, name, encoding=sys.getdefaultencoding(), metatextparser=None, assertCRLF=True):
        if assertCRLF and self.hasCRLF():
            raise Exception('One or more segments contain carriage return, which may cause problems as corpus in '
                            'plain-text formatted file')
        if not metatextparser:
            metatextparser = lambda x: x
        with codecs.open(name, 'w', encoding=encoding) as f:
            for s in self:
                f.write(metatextparser(s) + '\n')
        return self


class _TmxReader(object):
    def __init__(self, name):
        self._name = name
        self._buffer = ''

    def read_to(self, pattern, flags=0):
        for line in self._name:
            self._buffer += line
            m = re.search(pattern, self._buffer, flags=flags+re.U+re.S+re.M)
            if m:
                read = self._buffer[:m.start()]
                self._buffer = self._buffer[m.end():]
                return read
        return None


class BilingualSegmentList(list):
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
        super(BilingualSegmentList, self).__init__(seq)

    def __getslice__(self, i, j):
        return BilingualSegmentList(list.__getslice__(self, i, j))

    def __add__(self, other):
        return BilingualSegmentList(list.__add__(self, other))

    def __mul__(self, other):
        return BilingualSegmentList(list.__mul__(self, other))

    def __getitem__(self, item):
        element = list.__getitem__(self, item)
        if isinstance(item, slice):
            element = BilingualSegmentList(element)
        return element

    @staticmethod
    def _wh(key, target):
        return key in (target, 'both', 'any')

    def has_crlf(self):
        return any((SegmentList.find_crlf(s) or SegmentList.find_crlf(t)) for (s, t) in self)

    def catalog_chars(self, where='both', categories=None, detail=False):
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

    def _do_find(self, matcher, limit=0):
        res = []
        for i, (s, t) in enumerate(self):
            if matcher(s, t):
                res.append((i, s, t))
                if 0 < limit <= len(res):
                    break
        return res

    def _do_each(self, func):
        res = []
        for i, (s, t) in enumerate(self):
            newS, newT = func(s, t)
            if s != newS or t != newT:
                self[i] = (newS, newT)
                res.append((i, newS, newT))
        return res

    def trim(self, where='both'):
        funcS = SegmentList.trim_text if self._wh(where, 'source') else (lambda x: x)
        funcT = SegmentList.trim_text if self._wh(where, 'target') else (lambda x: x)
        return [(s, t) for (_, s, t) in self._do_each(lambda s, t: (funcS(s), funcT(t)))]

    def lower(self):
        return [(s, t) for (_, s, t) in self._do_each(lambda s, t: (s.lower(), t.lower()))]

    def tokenize(self, sourcetokenizer=None, targettokenizer=None):
        if not sourcetokenizer:
            sourcetokenizer = lambda x: x
        if not targettokenizer:
            targettokenizer = lambda x: x
        return [(s, t) for (_, s, t) in self._do_each(lambda s, t: (sourcetokenizer(s), targettokenizer(t)))]

    def cutoff(self, min=1, max=80, ratio=0):
        def evaluate(s, t):
            sc, tc = len(s.split()), len(t.split())
            if sc < min or tc < min or sc > max or tc > max:
                return True
            if ratio > 0 and (float(sc)/tc > ratio or float(tc)/sc > ratio):
                return True
            return False
        res = self._do_find(evaluate)
        for i in sorted((i for (i, s, t) in res), reverse=True):
            self.pop(i)
        return [(s, t) for (_, s, t) in res]

    def moses_escape(self):
        return self._do_each(lambda s, t: (SegmentList.moses_escape_text(s), SegmentList.moses_escape_text(t)))

    def moses_truecase(self, where='both', possibly_use_first_token=False,
                       source_model_name=None, target_model_name=None):
        if self._wh(where, 'source'):
            truecaser = MosesTruecaser().train((s for (s, t) in self), possibly_use_first_token=possibly_use_first_token)
            if source_model_name:
                truecaser.write(source_model_name)
            self._do_each(lambda s, t: (truecaser.truecase(s), t))
        if self._wh(where, 'target'):
            truecaser = MosesTruecaser().train((t for (s, t) in self), possibly_use_first_token=possibly_use_first_token)
            if target_model_name:
                truecaser.write(target_model_name)
            self._do_each(lambda s, t: (s, truecaser.truecase(t)))
        return self

    def _search(self, pattern, where='any', flags=0, limit=0):
        regex = re.compile(pattern, flags)
        funcS = (lambda x: regex.search(x)) if self._wh(where, 'source') else (lambda x: False)
        funcT = (lambda x: regex.search(x)) if self._wh(where, 'target') else (lambda x: False)
        func = (lambda x, y: funcS(x) and funcT(y)) if where == 'both' else (lambda x, y: funcS(x) or funcT(y))
        return self._do_find(func, limit=limit)

    def search_re(self, pattern, where='any', flags=0, limit=0):
        return [(s, t) for (_, s, t) in self._search(pattern, where=where, flags=flags, limit=limit)]

    def search(self, pattern, where='any', ignorecase=False, limit=0):
        return self.search_re(re.escape(pattern), where=where, flags=(re.I if ignorecase else 0), limit=limit)

    def replace_re(self, pattern, repl, where='both', flags=0):
        regex = re.compile(pattern, flags)
        funcS = (lambda x: regex.sub(repl, x)) if self._wh(where, 'source') else (lambda x: x)
        funcT = (lambda x: regex.sub(repl, x)) if self._wh(where, 'target') else (lambda x: x)
        return [(s, t) for (_, s, t) in self._do_each(lambda s, t: (funcS(s), funcT(t)))]

    def replace(self, pattern, repl, where='both', ignorecase=False):
        return self.replace_re(re.escape(pattern), repl, where=where, flags=(re.I if ignorecase else 0))

    def prune_re(self, pattern, where='any', flags=0):
        res = self._search(pattern, where=where, flags=flags, limit=0)
        pruned = [(s, t) for (_, s, t) in res]
        for i in sorted((i for (i, s, t) in res), reverse=True):
            self.pop(i)
        return pruned

    def prune(self, pattern, where='any', ignorecase=False):
        return self.prune_re(re.escape(pattern), where=where, flags=(re.I if ignorecase else 0))

    def empty(self, where='any', prune=False):
        funcS = (lambda x: len(x) == 0) if self._wh(where, 'source') else (lambda x: False)
        funcT = (lambda x: len(x) == 0) if self._wh(where, 'target') else (lambda x: False)
        func = (lambda s, t: funcS(s) and funcT(t)) if where == 'both' else (lambda s, t: funcS(s) or funcT(t))
        indices = [i for (i, s, t) in self._do_find(func)]
        if prune:
            for i in sorted(indices, reverse=True):
                self.pop(i)
        return len(indices)

    def duplicate(self, where='both', uniq=False):
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
        res = [[self[i] for i in indices] for indices in freq.itervalues() if len(indices) > 1]
        if uniq:
            for i in sorted((i for indices in freq.itervalues() for i in indices if len(indices) > 1), reverse=True):
                self.pop(i)
        return res

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
        elif format == 'tmx':
            assert isinstance(name, basestring), 'Parameter: name is NOT a string'
            return self._read_tmx(name, encoding=encoding, **kwargs)
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

    def write_text(self, sourcename, targetname,
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
                    fS.write(metatextparser(s) + '\n')
                    fT.write(metatextparser(t) + '\n')
        return self

    def _read_tmx(self, name, encoding=sys.getdefaultencoding(),
                  lang=('<UNKNOWN0>', '<UNKNOWN1>'),
                  metatextparser=None,
                  progresscallback=None,
                  verbose=False):
        """
        (Private method) Read segment text from a TMX file and append the current segment list.
        :param name: Filename
        :param encoding:
        :param lang:
        :param metatextparser:
        :param progresscallback:
        :param verbose:
        :return:
        """
        assert os.path.exists(name), 'TMX file does not exist.'

        filesize = os.path.getsize(name)
        lastprogressat = time.time()

        with codecs.open(name, 'r', encoding=encoding) as f:
            reader = _TmxReader(f)
            langS, langT = lang
            if not reader.read_to(r'<body>', re.I)[0]:
                raise Exception('Unexpected EOF - no <body>')
            else:
                while reader.read_to(r'<tu(\s.*?)*>', re.I+re.U):
                    TU = reader.read_to(r'</tu>', re.I)
                    if TU is None:
                        raise Exception('Unexpected EOF - no </tu>')
                    TUVs = re.findall(r'(<tuv(?:\s.*?)*>)(.*?)(</tuv>)', TU, re.I + re.U + re.S + re.M)
                    if len(TUVs) >= 2:
                        textS, textT = None, None
                        if langS == '<UNKNOWN0>':
                            m = re.search(r'xml:lang="(.*?)"', TUVs[0][0], re.I + re.U + re.S + re.M)
                            if m:
                                langS = m.group(1)
                        if langT == '<UNKNOWN1>':
                            m = re.search(r'xml:lang="(.*?)"', TUVs[1][0], re.I + re.U + re.S + re.M)
                            if m:
                                langT = m.group(1)
                        for ix, TUV in enumerate(TUVs):
                            m = re.search(r'xml:lang="(.*?)"', TUV[0], re.I + re.U + re.S + re.M)
                            lang = m.group(1) if m else '<UNKNOWN%s>' % ix
                            if lang == langS or lang == langT:
                                m = re.search(r'<seg(?:\s.*?)*>(.*?)</seg>', TUV[1], re.I + re.U + re.S + re.M)
                                if m:
                                    text = m.group(1).strip('\r\n')
                                    text = re.sub(r'<ph(?:\s.*?)*>(.*?)</ph>', '', text, re.I + re.U + re.S + re.M)
                                    text = re.sub(r'<ut>(.*)</ut>', '', text, re.I + re.U + re.S + re.M)
                                    text = text.replace(u'&apos;', u"'").replace(u'&quot;', u'"')\
                                        .replace(u'&lt;', u'<').replace(u'&gt;',u'>').replace(u'&amp;', u'&')
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


if __name__ == '__main__':
    from unicodeprint import unicodeprint
    from local_settings import myenv
    bslist = BilingualSegmentList()
    bslist.read(format='tmx', name=myenv.tmxV, encoding='utf-8', verbose=True)
    print(len(bslist))
    subset = bslist[100:110]
    print(type(subset))
    print(len(subset))
    unicodeprint.pprint(subset)
    unicodeprint.pprint(bslist.catalog_chars())
    unicodeprint.pprint(bslist.search_re(u'[\u57f7]'))
    bslist.replace_re(r'{\d+}', '')
    unicodeprint.pprint(len(bslist.trim()))
    unicodeprint.pprint(bslist.empty(prune=True))
    unicodeprint.pprint(bslist.search_re(u'^$'))
    unicodeprint.pprint(len(bslist))
    unicodeprint.pprint(len(bslist.duplicate(uniq=True)))
    unicodeprint.pprint(len(bslist))
    unicodeprint.pprint(bslist.cutoff())
    unicodeprint.pprint(len(bslist))
    print('tokenizing...')
    bslist.tokenize(sourcetokenizer=lambda x: ' '.join(nltk.word_tokenize(x)), targettokenizer=None)
    bslist.moses_escape()
    print('truecasing...')
    bslist.moses_truecase(where='source')
