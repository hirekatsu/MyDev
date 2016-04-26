# -*- coding: utf-8 -*-
import sys
import nltk
import codecs


class CaptalNormalizer():
    def __init__(self, ngram=5, freq_threshold=3, for_full=False, for_camel=False):
        self._dic = []
        self._ngram = ngram
        assert(self._ngram >= 1)
        self._freq_threshold = freq_threshold
        self._for_full = for_full
        self._for_camel = for_camel

    @staticmethod
    def _lower(text):
        if isinstance(text, unicode):
            return text.lower()
        return [t.lower() for t in text]

    @staticmethod
    def _isanyupper(text):
        if isinstance(text, unicode):
            return any(c for c in text)
        return any(CaptalNormalizer._isanyupper(t) for t in text)

    def read(self, filename, encoding=sys.getdefaultencoding()):
        with codecs.open(filename, 'r', encoding=encoding) as f:
            self.corpus(l for l in f)
        return self

    def corpus(self, lines):
        self._dic = []
        nphrs = []

        for l in lines:
            tkns = nltk.word_tokenize(l)


            for n in range(1, self._ngram + 1):
                phrs = tkns if n == 1 else list(nltk.ngrams(tkns, n))
                nphrs += [(self._lower(p), p) for p in phrs]
        pcfd = nltk.ConditionalFreqDist(nphrs)


        fd = nltk.FreqDist(nltk.word_tokenize(text))
        for token in fd:
            if any(c.isupper() for c in token):
                if all(c.isupper() for c in token):
                    if not self._for_full:
                        continue
                if not token[0].isupper():
                    if not self._for_camel:
                        continue
                lo = token.lower()
                if fd[lo] >= min(self._freq_threshold, fd[token]):
                    self._dic.append(token)
        return self

    def save(self, filename):
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            for token in self._dic:
                f.write(token + '\n')
        return self

    def load(self, filename):
        self._dic = []
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            self._dic = [l.strip() for l in f]
        return self

    def normalize(self, text):
        return text.lower() if text in self._dic else text

    def print_dic(self):
        print self._dic


# test
if __name__ == '__main__':
    with codecs.open(r'D:\DATA\PROJ\NLTK\160420_term\0.dlp.trn.en', 'r', encoding='utf-8') as f:
            print nltk.word_tokenize(f.read()[:100])
#    cn = CaptalNormalizer().read(r'D:\DATA\PROJ\NLTK\160420_term\0.dlp.trn.en', 'utf-8')


