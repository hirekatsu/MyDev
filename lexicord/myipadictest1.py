# -*- coding: utf-8 -*-
import subprocess
import codecs
import re
from lputils.BiText import BiText
import MeCab

tmxfilename = r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/vasont.tmx'
csvfilename = r'/Users/kiyoshi_izumi/Desktop/DATA/DEV/MyGitHub/MyDev/lexicord/mydic.csv'
dicfilename = r'/Users/kiyoshi_izumi/Desktop/DATA/DEV/MyGitHub/MyDev/lexicord/mydic.dic'
indexcommand = r'/usr/local/libexec/mecab/mecab-dict-index'

def myprogress(x):
    print '\r{0}% '.format(int(x * 100)), '*' * int(x * 25),

bt = BiText().readtmx(tmxfilename, encoding='utf-8', progresscallback=myprogress).trim()
bt.duplicate(uniq=True)
print '\r'

with codecs.open(csvfilename, 'r', encoding='utf-8') as f:
    keywords = [line.strip() for line in f]
existing = [line.split(',', 1)[0] for line in keywords]

while True:
    loop = None
    mt = MeCab.Tagger('-Owakati -u %s' % dicfilename)
    tokens = []
    for i, (_, t) in enumerate(bt):
        try:
            v = t.encode('utf-8')
        except Exception as e:
            continue
        x = mt.parse(v)
        tokens += unicode(x, 'utf-8').split()
    longest = sorted(set(tokens), key=lambda x: len(x), reverse=True)

    addition = []
    postcheck = []
    ix = 0
    while True:
        for i, t in enumerate(longest[ix:ix+20]):
            print u'{0: >3}: {1} ({2})'.format(i + ix, t, len(t))
        userinput = raw_input(u'action (l, N, g, q)? ').strip()
        if userinput == u'l':
            ix += 20
            continue
        if userinput == u'g':
            loop = 'continue'
            break
        if userinput == u'q':
            loop = 'break'
            break
        if not re.match(r'^\d+$', userinput):
            print u'UNKNOWN ACTION'
            continue
        i = int(userinput)
        t = longest[i]
        print u'customizing for {0: >3}: {1} ({2})'.format(i, t, len(t))
        while True:
            userinput = raw_input(u'action (N:N, n, g, q)? ').strip()
            if userinput == u'n':
                break
            if userinput == u'g':
                loop = 'continue'
                break
            if userinput == u'q':
                loop = 'break'
                break
            if not re.match(r'^\d+:\d+$', userinput):
                print u'UNKNOWN ACTION'
                continue
            (start, end) = userinput.split(':')
            keyword = t[int(start):int(end)]
            userinput = raw_input(u'append {0} (y, n)? '.format(keyword)).strip()
            if userinput == u'y':
                addition.append(keyword)
                postcheck.append(t)
        if loop in ('continue', 'break'):
            break
    if loop == 'break':
        break

    for k in sorted(addition):
        print k
    ucom = raw_input(u'append to dic (y, n)? ').strip()
    if ucom == u'y':
        keywords += [u'{0},,,1,名詞,一般,*,*,*,*,{0},{0},'.format(k) for k in addition if k not in existing]
        keywords.sort()
        with codecs.open(csvfilename, 'w', encoding='utf-8') as f:
            for line in keywords:
                f.write(line + u'\n')
        p = subprocess.Popen(u'{0} -d /usr/local/lib/mecab/dic/ipadic -u {1} -f utf-8 -t utf-8 {2}'.format(
            indexcommand, dicfilename, csvfilename), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        comout, comerr = p.communicate()
        print comout
        print comerr

        mt = MeCab.Tagger('-Owakati -u %s' % dicfilename)
        for t in set(postcheck):
            print u'  {0}'.format(unicode(mt.parse(t.encode('utf-8')), 'utf-8'))
    else:
        ucom = raw_input(u'continue? (y, n) ').strip()
        if ucom != u'y':
            break


