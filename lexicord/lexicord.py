# -*- coding: utf-8 -*-
import nltk
import codecs
from nltk import FreqDist, ConditionalFreqDist
from lputils import isstoptoken_en, isstoptoken_ja
from lputils.CapsNormalizer import CapsNormalizer


def toklen(t):
    return 1 if isinstance(t, unicode) else len(t)


def tokstr(t):
    return t if isinstance(t, unicode) else u' '.join(t)


maxN = 5
filenameE = r'D:\DATA\PROJ\NLTK\160420_term\0.dlp.trn.en'
filenameJ = r'D:\DATA\PROJ\NLTK\160420_term\0.dlp.trn.ja'

f = codecs.open(filenameE, 'r', 'utf-8')
tokE = [nltk.word_tokenize(l.strip()) for l in f]
f = codecs.open(filenameJ, 'r', 'utf-8')
tokJ = [nltk.word_tokenize(l.strip()) for l in f]
assert(len(tokE) == len(tokJ))
print 'total: %s line(s)' % len(tokE)

cops = {}
for nx in range(1, maxN + 1):
    cops[nx] = []
eo = FreqDist()

ii = 0
while ii < min(len(tokE), 4000):
    tE = [t.lower() for t in tokE[ii]]
    tJ = tokJ[ii]
    pE = {1: set([t for t in tE if not isstoptoken_en(t)])}
    pJ = {1: set([t for t in tJ if not isstoptoken_ja(t)])}
    for t in pE[1]:
        eo[t] += 1
    for nx in range(2, maxN + 1):
        pE[nx] = set([t for t in nltk.ngrams(tE, nx) if not isstoptoken_en(t)])
        pJ[nx] = set([t for t in nltk.ngrams(tJ, nx) if not isstoptoken_ja(t)])
        for t in pE[nx]:
            eo[t] += 1
    for ne in range(1, maxN + 1):
        for nj in range(1, maxN + 1):
            cops[ne].extend((e, j) for e in pE[ne] for j in pJ[nj])
    ii += 1
    if ii % 40 == 0:
        print '.',
print ''

print 'removing duplicates...'
cfds = {}
for n, v in cops.iteritems():
    cfds[n] = ConditionalFreqDist(v)
for ne in range(2, maxN + 1):
    for e in cfds[ne].conditions():
        n = cfds[ne][e].N()
        subsets = nltk.ngrams(e, ne - 1) if ne > 2 else e
        for subset in subsets:
            if cfds[ne - 1][subset].N() == n:
                cfds[ne - 1].pop(subset)

cop = []
for v in cops.itervalues():
    cop.extend(v)
cfd = ConditionalFreqDist(cop)

print '-' * 40
# print [item for item in cfd.iteritems()]
# print [item for item in fd.iteritems()]
fff = FreqDist()

freqterms = {}
for e, fd in cfd.iteritems():
    o = eo[e]
    freqterms[(e, o, toklen(e))] = sorted([(j, f, float(f) / o if o > 0 else -1, toklen(j)) for j, f in fd.iteritems()], key=lambda x: x[1] * 1000 + x[3], reverse=True)
freqterms = sorted(freqterms.items(), key=lambda x: x[1][0][1], reverse=True)
for e, fd in freqterms:
    if fd[0][1] < 30:
        break
    print '%s == %s : %s (%s)' % (tokstr(e[0]), tokstr(fd[0][0]), fd[0][1], fd[0][2])

print '-' * 40
possibles = sorted(freqterms, key=lambda x: x[1][0][2], reverse=True)
for e, fd in possibles:
    if fd[0][2] < 0.8:
        break
    if e[1] >= 10:
        print '%s == %s : %s (%s)' % (tokstr(e[0]), tokstr(fd[0][0]), fd[0][1], fd[0][2])
