# -*- coding: utf-8 -*-
import nltk
import codecs
from nltk import FreqDist, ConditionalFreqDist
from lputils import isstoptoken_en, isstoptoken_ja
from lputils.CaptalNormalizer import CaptalNormalizer
from lputils.BiCorpus import BiCorpus
import MeCab

mt = MeCab.Tagger()
print mt.parse("私の名前は鈴木花子です。")

