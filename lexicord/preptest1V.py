# -*- coding: utf-8 -*-
from local_settings import myenv
from lputils.segmentlist import BilingualSegmentList
from lputils.unicodeprint import unicodeprint as up

bsl = BilingualSegmentList()
bsl.read(format='tmx', name=myenv.tmxV, encoding='utf-8', verbose=True)
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

# bsl.writetext(myenv.tmxV+'.en', myenv.tmxV+'.ja', sourceencoding='utf-8', targetencoding='utf-8', forcewithcr=False)

import nltk
import MeCab

mtagger = MeCab.Tagger('-Owakati -u %s' % myenv.projfile('mydic.dic'))

def sourcetokenize(text):
    return u' '.join(nltk.word_tokenize(text))

def targettokenize(text):
    return mtagger.parse(text.encode('utf-8')).decode('utf-8').strip()

bsl.tokenize(sourcetokenize, targettokenize)
bsl.moses_escape()
bsl.moses_truecase(where='source', source_model_name=myenv.tmxV+'.truecasemodel.en')

# import random
# random.shuffle(bsl)
#
# trnmax = int(1.0 * len(bsl) * 0.9)
# tunmax = int(1.0 * len(bsl) * 0.95)
# training = bsl[:trnmax]
# training.cutoff()
# training.writetext(myenv.tmxV+'.trn.en', myenv.tmxV+'.trn.ja',
#                    sourceencoding='utf-8', targetencoding='utf-8')
# bsl[trnmax:tunmax].writetext(myenv.tmxV+'.tun.en', myenv.tmxV+'.tun.ja',
#                              sourceencoding='utf-8', targetencoding='utf-8')
# bsl[tunmax:].writetext(myenv.tmxV+'.eva.en', myenv.tmxV+'.eva.ja',
#                        sourceencoding='utf-8', targetencoding='utf-8',)
