# -*- coding: utf-8 -*-
# import nltk
# import codecs
# from nltk import FreqDist, ConditionalFreqDist
# from lputils import isstoptoken_en, isstoptoken_ja
# from lputils.CapsNormalizer import CapsNormalizer
# from lputils.BiCorpus import BiCorpus
# import MeCab
import subprocess

csvfilename = r'/Users/kiyoshi_izumi/Desktop/DATA/DEV/MyGitHub/MyDev/lexicord/mydic.csv'
dicfilename = r'/Users/kiyoshi_izumi/Desktop/DATA/DEV/MyGitHub/MyDev/lexicord/mydic2.dic'
indexcommand = r'/usr/local/libexec/mecab/mecab-dict-index'

shellcommand = u'{0} -d /usr/local/lib/mecab/dic/ipadic -u {1} -f utf-8 -t utf-8 {2}'.format(indexcommand,
    dicfilename, csvfilename)
print shellcommand
p = subprocess.Popen(shellcommand, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
comout, comerr = p.communicate()
print comout
print comerr
