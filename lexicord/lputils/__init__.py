# -*- coding: utf-8 -*-


def __isstopchar_en(s):
    if s.isalnum():
        return False
    if s == '-':
        return False
    return True


def __isstopchar_ja(s):
    if s < u'\u2000':
        return __isstopchar_en(s)
    if s < u'\u3041':
        return True
    if s == u'\u30A0':
        return True
    if u'\u3220' <= s < u'\u3400':
        return True
    if u'\uFB00' < s:
        return True
    return False


def __isstopword_en(s):
    if s.isdigit():
        return True
    return s in (u'a', u'and', u'are', u'be', u'can', u'do', u'does', u'for', u'from', u'if', u'in', u'is', u'must', u'of', u'on', u'or', u'should', u'that', u'the', u'this', u'to', u'under', u'up', u'what', u'when', u'where', u'which', u'while', u'why', u'will', u'with', u'you', u'your')


def __isstopword_ja(s):
    if s.isdigit():
        return True
    return s in (u'が', u'から', u'さ', u'し', u'で', u'でき', u'と', u'に', u'について', u'の', u'は', u'へ', u'ます', u'ませ', u'れ', u'を', u'ん')


def isstoptoken_en(s):
    if isinstance(s, unicode):
        return __isstopchar_en(s) or __isstopword_en(s)
    else:
        if any(__isstopchar_en(t) for t in s):
            return True
        if __isstopword_en(s[0]) or __isstopword_en(s[-1]):
            return True
        return all(__isstopword_en(t) for t in s)


def isstoptoken_ja(s):
    if isinstance(s, unicode):
        return __isstopchar_ja(s) or __isstopword_ja(s)
    else:
        if any(__isstopchar_ja(t) for t in s):
            return True
        if __isstopword_ja(s[0]) or __isstopword_ja(s[-1]):
            return True
        return all(__isstopword_ja(t) for t in s)


def sliceof(small, big):
    for i in xrange(len(big)-len(small)+1):
        for j in xrange(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return i, i+len(small)
    return False
