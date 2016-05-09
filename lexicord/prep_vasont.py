# -*- coding: utf-8 -*-
from lputils.BiText import BiText

bt = BiText()
bt.readtmx(r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/vasont.tmx', encoding='utf-8')
bt.trim(True, True, True)
bt.empty(where='any', prune=True)
bt.duplicate(where='both', uniq=True)
size = bt.count()
print size

bt.prune(u'[\u203B\u25CE\u2605\u2666\u3010\u3011]', regex=True)
bt.replace(u'[\u2028\u25B2\uFF4A]', u'', regex=True)
bt.replace(u'[\u00A0\u200B\u3000]', u' ', regex=True)
bt.replace(u'\uFF11', u'1')
bt.replace(u'\uFF54\uFF4C\uFF53', u'tls')
bt.replace(u'\uFF27', u'G')
bt.replace(u'\uFF29\uFF30', u'IP')
bt.duplicate(where='both', uniq=True)

# bt.writetext(r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/vasont.en', r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/vasont.ja', sourceencoding='utf-8', targetencoding='utf-8', forcewithcr=False)

import nltk
import MeCab

mtagger = MeCab.Tagger('-Owakati -u /Users/kiyoshi_izumi/Desktop/DATA/DEV/MyGitHub/MyDev/lexicord/mydic.dic')

def sourcetokenize(text):
    return u' '.join(nltk.word_tokenize(text))

def targettokenize(text):
    return mtagger.parse(text.encode('utf-8')).decode('utf-8').strip()

bt.tokenize(sourcetokenize, targettokenize)

trainingmax = int(1.0 * bt.count() * 0.9)
tuningmax = int(1.0 * bt.count() * 0.95)
bt.writetext(r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/vasont.trn.en', r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/vasont.trn.ja', sourceencoding='utf-8', targetencoding='utf-8', metatextparser=BiText.escape_moses_special_char, end=trainingmax)
bt.writetext(r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/vasont.tun.en', r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/vasont.tun.ja', sourceencoding='utf-8', targetencoding='utf-8', metatextparser=BiText.escape_moses_special_char, start=trainingmax, end=tuningmax)
bt.writetext(r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/vasont.eva.en', r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/vasont.eva.ja', sourceencoding='utf-8', targetencoding='utf-8', metatextparser=BiText.escape_moses_special_char, start=tuningmax)

