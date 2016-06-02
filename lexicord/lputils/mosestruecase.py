# -*- coding: utf-8 -*-
from collections import defaultdict
import codecs
import re


class MosesTruecaser(object):
    """
    Class of moses truecaser (train-model and truecase)

    https://github.com/moses-smt/mosesdecoder/tree/master/scripts/recaser
    - train-truecase.perl
    - truecase.perl
    """
    _sentence_end = (u'.', u':', u'?', u'!')
    _delayed_sentence_start = (u'(', u'[', u'"', u",", u'&apos;', u'&quot;', u'&#91;', u'&#93')

    def __init__(self):
        self.reset()

    def _build(self):
        """
        (private method) Build _best and _known dictionaries from _casing list.
        :return: The object itself.
        """
        self._best = {}
        self._known = {}
        for words in self._casing.itervalues():
            for i, (word, _) in enumerate(sorted(words.items(), key=lambda x: x[1], reverse=True)):
                if i == 0:
                    self._best[word.lower()] = word
                self._known[word] = 1
        return self

    def reset(self):
        """
        Reset and initialize the truecase model.
        :return: The object itself.
        """
        self._casing = defaultdict(lambda: defaultdict(float))
        self._best = {}
        self._known = {}
        return self

    def train(self, sentences, possibly_use_first_token=False):
        """
        Train the truecaser model.
        This method can be called cumulatively.
        :param sentences: List of sentences. A sentence has to be a string or a list of tokens.
        When a string, the sentence is expected to be already tokenized.
        :param possibly_use_first_token: When True, the first word of a sentence is evaluated.
        :return: The object itself.
        """
        for sentence in sentences:
            words = sentence.split() if isinstance(sentence, basestring) else sentence
            assert hasattr(words, '__iter__'), 'Type of element in sentences is NOT string or iterable.'
            first_of_sentence = True
            for word in words:
                weight = 0.0
                if not first_of_sentence:
                    weight = 1.0
                elif possibly_use_first_token:
                    first_char = word[0]
                    if first_char.islower():
                        weight = 1.0
                    elif len(words) == 1:
                        weight = 0.1
                if weight > 0:
                    self._casing[word.lower()][word] += weight
                if word in self._sentence_end:
                    first_of_sentence = True
                elif word not in self._delayed_sentence_start:
                    first_of_sentence = False
        self._build()
        return self

    def read(self, filename):
        """
        Read the truecase model from a file. The expected encoding is UTF-8.
        The read info is stored cumulatively in this object.
        :param filename: Filename (path and filename).
        :return: The object itself.
        """
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            for l in f:
                items = l.strip().split()
                if len(items) > 1:
                    assert items[1].startswith(u'(') and items[1].endswith(u')'), 'Unexpected score/total format. (1)'
                    assert u'/' in items[1], 'Unexpected score/total format. (2)'
                    words = self._casing[items[0].lower()]
                    words[items[0]] += float(items[1][1:-1].split(u'/', 1)[0])
                    for i in range(2, len(items), 2):
                        assert items[i+1].startswith(u'(') and items[i+1].endswith(u')'), 'Unexpected score format.'
                        words[items[i]] += float(items[i+1][1:-1])
        self._build()
        return self

    def write(self, filename):
        """
        Write the truecase model in a file. The encoding is UTF-8.
        :param filename: Filename (path and filename).
        :return: The object itself.
        """
        def f2s(v):
            v = str(v)
            return v[:-2] if v.endswith('.0') else v

        with codecs.open(filename, 'w', encoding='utf-8') as f:
            for words in self._casing.itervalues():
                total = sum(words.itervalues())
                words = sorted(words.items(), key=lambda x: x[1], reverse=True)
                f.write(u'{0} ({1}/{2})'.format(words[0][0], f2s(words[0][1]), f2s(total)))
                if len(words) > 1:
                    f.write(u' ' + u' '.join([u'{0} ({1})'.format(w, f2s(s)) for (w, s) in words[1:]]))
                f.write(u'\n')
        return self

    def truecase(self, sentence):
        """
        Apply the casing based on the trained-model.
        :param sentence: A sentence string.
        :return: The casing-modified string.
        """
        words, markups = self.split_xml(sentence)
        start_of_sentence = True
        result = []
        for i in range(len(words)):
            if i > 0 and markups[i] == '':
                result.append(' ')
            result.append(markups[i])
            m = re.match(r'([^\|]+)(.*)', words[i])
            if m:
                word, factors = m.group(1), m.group(2)
            else:
                word, factors = words[i], u''
            if start_of_sentence and word.lower() in self._best:
                result.append(self._best[word.lower()])
            elif word in self._known:
                result.append(word)  # don't change know words
            elif word.lower() in self._best:
                result.append(self._best[word.lower()])
            else:
                result.append(word)  # unknown, nothing to do
            result.append(factors)
            if word in self._sentence_end:
                start_of_sentence = True
            elif word not in self._delayed_sentence_start:
                start_of_sentence = False
        result.append(markups[-1])
        return ''.join(result)

    @staticmethod
    def split_xml(line):
        words = []
        markups = ['']
        i = 0
        while re.search(r'\S', line):
            m = re.search(r'^\s*(<\S[^>]*>)(.*)$', line)
            # XML tag
            if m:
                potential_xml, line_next = m.group(1), m.group(2)
                # exception for factor that is an XML tag
                if re.search(r'^\S', line) and len(words) > 0 and words[-1][-1] == '|':
                    words[-1] += potential_xml
                    m = re.search(r'^(\|+)(.*)$', line_next)
                    if m:
                        words[-1] += m.group(1)
                        line_next = m.group(2)
                else:
                    markups.append(potential_xml + ' ')
                line = line_next
            else:
                m = re.search(r'^\s*([^\s<>]+)(.*)$', line)
                # non-XML text
                if m:
                    words.append(m.group(1))
                    markups.append('')
                    line = m.group(2)
                else:
                    m = re.search(r'^\s*(\S+)(.*)$', line)
                    # '<' or '>' occurs in word, but it's not an XML tag
                    assert m is not None, 'Unexpected sequence of text to split, huh? ' + line
                    words.append(m.group(1))
                    markups.append('')
                    line = m.group(2)
        markups[-1] = markups[-1][:-1]
        return words, markups


