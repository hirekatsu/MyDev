# -*- coding: utf-8 -*-
import sys
import codecs
import re


class BiCorpus():
    def __init__(self):
        self._sents = []
        self._sentt = []

    def source(self):
        return self._sents

    def target(self):
        return self._sentt

    def count(self):
        return len(self._sents)

    def __getitem__(self, index):
        return self._sents[index], self._sentt[index]

    def readtext(self, fnames, fnamet, encodings=sys.getdefaultencoding(), encodingt=sys.getdefaultencoding()):
        self._sents = []
        self._sentt = []
        with codecs.open(fnames, 'r', encoding=encodings) as f:
            self._sents = [l.strip() for l in f]
        with codecs.open(fnamet, 'r', encoding=encodingt) as f:
            self._sentt = [l.strip() for l in f]
        assert(len(self._sents) == len(self._sentt))
        return self

    def readtmx(self, tmxname, encoding=sys.getdefaultencoding(),
                sourcelanguage='UNKNOWN0', targetlanguage='UNKNOWN1',
                metatextconvert=None):
        self._sents = []
        self._sentt = []
        with codecs.open(tmxname, 'r', encoding=encoding) as f:
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
                                if metatextconvert:
                                    segtext = metatextconvert(segtext)
                                if tuvlang == langs:
                                    texts = segtext
                                if tuvlang == langt:
                                    textt = segtext
                    if texts is not None and textt is not None:
                        self._sents.append(texts)
                        self._sentt.append(textt)
        return self
