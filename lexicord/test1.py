# -*- coding: utf-8 -*-
import nltk
import codecs
from nltk import FreqDist, ConditionalFreqDist
from lputils import isstoptoken_en, isstoptoken_ja
from lputils.CapsNormalizer import CapsNormalizer
from lputils.BiCorpus import BiCorpus
import MeCab

def myprogress(x):
    print '.',
cn = CapsNormalizer().read(r'D:\DATA\PROJ\NLTK\160420_term\0.dlp.trn.en', 'utf-8', progresscallback=myprogress)
for t in cn._capsdict[0:30]:
    print t
cn.save(r'D:\DATA\PROJ\NLTK\160420_term\0.normalize.en')
cn.load(r'D:\DATA\PROJ\NLTK\160420_term\0.normalize.en')
print cn.normalize(u'Size filters are only available for files on file shares , Endpoint files , Lotus Notes documents , SharePoint items , and Exchange items .'.split())


