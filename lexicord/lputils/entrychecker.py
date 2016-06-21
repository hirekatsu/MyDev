# -*- coding: utf-8 -*-

import re
import copy
import codecs


class _EntBase(object):
    def __init__(self, expression, regex, boundary, ignorecase, comment=u'', source=u''):
        flags = re.I if ignorecase else 0
        pattern = expression if regex else re.escape(expression)
        if boundary:
            pattern = ur'\b' + pattern + ur'\b'
        self._re = re.compile(pattern, flags+re.U+re.M)
        self.display = expression
        self.comment = comment
        self.source = source

    def search(self, text, pos=0):
        return self._re.search(text, pos)


class MonoEntry(_EntBase):
    def __init__(self, expression, regex, boundary, ignorecase, comment, source):
        super(MonoEntry, self).__init__(expression, regex, boundary, ignorecase, comment, source)
        self._exceptions = []

    def exception(self, expression, regex, boundary, ignorecase, comment, source):
        self._exceptions.append(_EntBase(expression, regex, boundary, ignorecase, comment, source))

    def search(self, text, pos=0):
        m = super(MonoEntry, self).search(text, pos)
        if m:
            for ex in self._exceptions:
                xm = ex.search(text, pos)
                if xm and xm.start <= m.start and xm.end >= m.end:
                    m = None
                    break
        return m


class ParaEntry(_EntBase):
    def __init__(self, sexpression, sregex, sboundary, signorecase,
                 texpression, tregex, tboundary, tignorecase, comment, source):
        super(ParaEntry, self).__init__(sexpression, sregex, sboundary, signorecase, comment, source)
        self.target = _EntBase(texpression, tregex, tboundary, tignorecase)


class _CheckerBase(object):
    def __init__(self):
        self._entries = []
        self._sourcelist = []

    def _add_source(self, name):
        self._sourcelist.append(name)
        return len(self._sourcelist) - 1

    def _unpack_source(self, source):
        c = source.split(u':', 1)
        source_id = int(c[0])
        if source_id < len(self._sourcelist):
            source = self._sourcelist[source_id]
            if len(c) > 1:
                source += u':' + c[1]
        return source

    def _check_one(self, text, pos, entries):
        match, entry = None, None
        for e in entries:
            m = e.search(text, pos)
            if m:
                if not match or m.start < match.start or (m.start == match.start and m.end > match.end):
                    match = m
                    entry = e
            else:
                entries.remove(e)
        return match, entry


class MonoChecker(_CheckerBase):
    def __init__(self):
        super(MonoChecker, self).__init__()

    def check(self, text):
        results = []
        pos = 0
        entries = copy.deepcopy(self._entries)
        while len(entries) > 0:
            match, entry = self._check_one(text, pos, entries)
            if match:
                results.append((match.start, match.end,
                                entry.display, entry.comment, self._unpack_source(entry.source)))
        return results

    def load(self, name):
        source_id = self._add_source(name)
        default_ignorecase = False
        default_regex = False
        default_boundary = False
        with codecs.open(name, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.startswith('#'):
                    break
                if line.startswith('#option:'):
                    option = [c.strip() for c in (line[len('#option:'):].split('=', 1) + [''])]
                    if option[0] == 'ignorecase' and option[1] == 'yes':
                        default_ignorecase = True
                    if option[0] == 'regex' and option[1] == 'yes':
                        default_regex = True
                    if option[0] == 'boundary' and option[1] == 'yes':
                        default_boundary = True

        def read_flags(flags):
            return (default_ignorecase, default_regex, default_boundary)

        tabsep = re.compile(u'\t+')
        entry = None
        with codecs.open(name, 'r', encoding='utf-8') as f:
            for ln, lc in enumerate(unicode(l.rstrip()) for l in f):
                if len(lc) == 0 or lc.startswith(u'#'):
                    continue
                body, comment = (lc.split(u'\t#', 1) + [u''])[:2]
                columns = tabsep.split(body) + [u'', u'']
                if not columns[0]:
                    (ignorecase, regex, boundary) = read_flags('')
                    entry = MonoEntry(columns[0], regex, boundary, ignorecase, comment, u'{}:{}'.format(source_id, ln))
                    self._entries.append(entry)
                else:
                    if columns[1] != u'X':
                        raise Exception(u'Unknown modifier: {} @ line# {}: {}'.format(columns[1], ln, name))
                    if not columns[2]:
                        raise Exception(u'Empty entry text: {} @ line# {}: {}'.format(columns[1], ln, name))
                    if entry:
                        (ignorecase, regex, boundary) = read_flags('')
                        entry.exception(columns[2], regex, boundary, ignorecase, comment, u'{}:{}'.format(source_id, ln))


class ParaChecker(_CheckerBase):
    def __init__(self):
        super(ParaChecker, self).__init__()

    def check(self, stext, ttext):
        results = []
        pos = 0
        entries = copy.deepcopy(self._entries)
        while len(entries) > 0:
            match, entry = self._check_one(stext, pos, entries)
            if match:
                if not entry.target.search(ttext):
                    results.append((match.start, match.end,
                                    entry.display, entry.target.display, entry.comment,
                                    self._unpack_source(entry.source)))

