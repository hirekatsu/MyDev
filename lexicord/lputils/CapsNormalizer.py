# -*- coding: utf-8 -*-
import sys
import nltk
import codecs


class CapsNormalizer():
    def __init__(self, ngram=5, freqthreshold=3, title=False, camel=False):
        self._capsdict = []
        self._ngram = ngram
        assert(self._ngram >= 1)
        self._freqthreshold = freqthreshold
        self._title = title
        self._camel = camel

    @staticmethod
    def _lower(text):
        """
        Change all uppercase characters to lower.
        :param text:
        :type text: basestring or tuple
        :return: Changed string or list of strings.
        :rtype: basestring or tuple
        """
        return text.lower() if isinstance(text, basestring) else tuple(t.lower() for t in text)

    @staticmethod
    def _istokentonormalize(text):
        """
        Check if the text contains one or more uppercase characters. \
        If the input is a list, return True if the condition is true for all elements in the list.
        :param text:
        :type text: basestring or tuple
        :return:True if the conditions match
        :rtype: bool
        """
        return any(c.isupper() for c in text) if isinstance(text, basestring) \
            else all(CapsNormalizer._istokentonormalize(t) for t in text)

    @staticmethod
    def _isanylower(text):
        return any(c.islower() for c in text) if isinstance(text, basestring) \
            else any(CapsNormalizer._isanylower(t) for t in text)

    @staticmethod
    def _iscamel(text):
        return any(c.isupper() for c in text[1:]) if isinstance(text, basestring) \
            else all(CapsNormalizer._iscamel(t) for t in text)

    @staticmethod
    def _toklen(text):
        return 1 if isinstance(text, basestring) else len(text)

    def read(self, filename, encoding=sys.getdefaultencoding(), progresscallback=None):
        with codecs.open(filename, 'r', encoding=encoding) as f:
            self.corpus((l for l in f), progresscallback=progresscallback)
        return self

    def corpus(self, lines, progresscallback=None):
        self._capsdict = []

        if progresscallback:
            import time
            elapsed = 0.0
            lastcallat = time.time()

        ngramlist = []
        for i, line in enumerate(lines):
            tokenlist = nltk.word_tokenize(line)
            ngramlist += [(token,) for token in tokenlist]
            for n in range(2, self._ngram + 1):
                ngramlist += list(nltk.ngrams(tokenlist, n))

            if progresscallback:
                if time.time() - lastcallat >= 1.0:
                    elapsed += (1.0 - elapsed) * 0.3
                    progresscallback(elapsed * 0.5)
                    lastcallat = time.time()
        cfd = nltk.ConditionalFreqDist((CapsNormalizer._lower(ngram), ngram) for ngram in ngramlist)
        if progresscallback:
            progresscallback(0.5)
            lastcallat = time.time()

        uniqngramlist = set(ngramlist)
        for i, ngram in enumerate(uniqngramlist):
            if ngram not in self._capsdict and CapsNormalizer._istokentonormalize(ngram):
                if not self._title and not CapsNormalizer._isanylower(ngram):
                    self._capsdict.append(tuple(ngram))
                elif not self._camel and CapsNormalizer._iscamel(ngram):
                    self._capsdict.append(tuple(ngram))
                else:
                    thefd = cfd[CapsNormalizer._lower(ngram)]
                    if thefd[ngram] >= self._freqthreshold and thefd.N() - thefd[ngram] < self._freqthreshold:
                        self._capsdict.append(tuple(ngram))

            if progresscallback:
                if time.time() - lastcallat >= 1.0:
                    progresscallback(float(i) / len(uniqngramlist) * 0.5 + 0.5)
                    lastcallat = time.time()

        self._capsdict.sort(key=CapsNormalizer._toklen, reverse=True)
        return self

    def save(self, filename):
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            for tokens in self._capsdict:
                f.write(u' '.join(tokens) + '\n')
        return self

    def load(self, filename):
        self._capsdict = []
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            self._capsdict = [tuple(l.strip().split()) for l in f]
        return self

    def normalize(self, tokenlist):
        normalized = []
        i = 0
        while i < len(tokenlist):
            for n in range(self._ngram, 0, -1):
                if i + n > len(tokenlist):
                    continue
                ngram = tokenlist[i:i+n]
                if tuple(ngram) in self._capsdict:
                    normalized += ngram
                    i += n
                    break
            else:
                normalized.append(tokenlist[i].lower())
                i += 1
        return normalized

    def _capsdict(self):
        print self._capsdict


# test
if __name__ == '__main__':
    def myprogress(x):
        print '\r{0:.2f} '.format(x) + '*' * int(x * 25),
    cn = CapsNormalizer().read(r'D:\DATA\PROJ\NLTK\160420_term\dlp.trn.en', 'utf-8', progresscallback=myprogress)
    for t in cn._capsdict[0:30]:
        print t
    cn.save(r'D:\DATA\PROJ\NLTK\160420_term\0.normalize.en')
    cn.load(r'D:\DATA\PROJ\NLTK\160420_term\0.normalize.en')
    print cn.normalize(u'Size filters are only available for files on file shares , Endpoint files , Lotus Notes documents , SharePoint items , and Exchange items .'.split())

