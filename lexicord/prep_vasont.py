# -*- coding: utf-8 -*-
from lputils.segmentlist import BilingualSegmentList
from lputils.unicodeprint import unicodeprint as up

bsl = BilingualSegmentList()
bsl.read(format='tmx', name=r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/vasont.tmx',
         encoding='utf-8', verbose=True)
print len(bsl)

bsl.replace_re(r'{\d+}', '')
bsl.prune_re(u'[\u203B\u25CE\u2605\u2666\u3010\u3011]')
bsl.replace_re(u'[\u2028\u25B2\uFF4A]', u'')
bsl.replace_re(u'[\u00A0\u200B\u3000]', u' ')
bsl.replace(u'\uFF11', u'1')
bsl.replace(u'\uFF54\uFF4C\uFF53', u'tls')
bsl.replace(u'\uFF27', u'G')
bsl.replace(u'\uFF29\uFF30', u'IP')
bsl.trim()
bsl.empty(prune=True)
bsl.duplicate(where='both', uniq=True)
print len(bsl)

# bsl.writetext(r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/vasont.en', r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/vasont.ja', sourceencoding='utf-8', targetencoding='utf-8', forcewithcr=False)

import nltk
import MeCab

mtagger = MeCab.Tagger('-Owakati -u /Users/kiyoshi_izumi/Desktop/DATA/DEV/MyGitHub/MyDev/lexicord/mydic.dic')

def sourcetokenize(text):
    return u' '.join(nltk.word_tokenize(text))

def targettokenize(text):
    return mtagger.parse(text.encode('utf-8')).decode('utf-8').strip()

bsl.tokenize(sourcetokenize, targettokenize)
bsl.moses_escape()
bsl.moses_truecase(where='source', sourcemodelfilename=r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/vasont.truecasemodel.en')

# import random
# random.shuffle(bsl)
#
# trnmax = int(1.0 * len(bsl) * 0.9)
# tunmax = int(1.0 * len(bsl) * 0.95)
# training = bsl[:trnmax]
# training.cutoff()
# training.writetext(r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/vasont.trn.en',
#                    r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/vasont.trn.ja',
#                    sourceencoding='utf-8', targetencoding='utf-8')
# bsl[trnmax:tunmax].writetext(r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/vasont.tun.en',
#                              r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/vasont.tun.ja',
#                              sourceencoding='utf-8', targetencoding='utf-8')
# bsl[tunmax:].writetext(r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/vasont.eva.en',
#                        r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/vasont.eva.ja',
#                        sourceencoding='utf-8', targetencoding='utf-8',)
