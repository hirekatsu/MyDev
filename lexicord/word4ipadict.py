# -*- coding: utf-8 -*-
import argparse
import os.path
import subprocess
import codecs
import re
from lputils.segmentlist import BilingualSegmentList
import MeCab

parser = argparse.ArgumentParser(description='Look up long words in TMX and maintain your IPA user dictionary.')
parser.add_argument('--tmx', '-t', required=True, action='store', type=str, help='a TMX file')
parser.add_argument('--encoding', '-e', action='store', type=str, default='utf-16', help='TMX file\'s encoding')
parser.add_argument('--dict', '-d', action='store', type=str, help='your IPA user dictionary file')
parser.add_argument('--csv', '-c', action='store', type=str, help='your user dictionary\'s intermediate csv file')
parser.add_argument('--index', '-i', action='store', type=str, help='mecab-dict-index command path')
parser.add_argument('--noascii', action='store_true', default=False,
                    help='pick up words consisting of non-ascii characters only')
args = parser.parse_args()

bsl = BilingualSegmentList().read(format='tmx', name=args.tmx, encoding=args.encoding, verbose=True)
bsl.trim()
bsl.duplicate(where='both', uniq=True)

if os.path.exists(args.csv):
    with codecs.open(args.csv, 'r', encoding='utf-8') as f:
        entries = [line.strip().split(',') for line in f]
    user_words = {items[0]: items for items in entries}
else:
    user_words = {}

tagger = MeCab.Tagger('-Owakati -u %s' % args.dict)


def update_userdic():
    global user_words
    with codecs.open(args.csv, 'w', encoding='utf-8') as f:
        for word in sorted(user_words.keys()):
            f.write(','.join(user_words[word]) + u'\n')
    p = subprocess.Popen(u'{0} -d /usr/local/lib/mecab/dic/ipadic -u {1} -f utf-8 -t utf-8 {2}'.format(
        args.index, args.dict, args.csv), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    comout, comerr = p.communicate()
    print comout
    print comerr
    return MeCab.Tagger('-Owakati -u %s' % args.dict)


def uinput(prompt):
    return unicode(raw_input(prompt).strip(), 'utf-8')


while True:
    loop = None
    tokens = []
    for i, (s, t) in enumerate(bsl):
        tokens += unicode(tagger.parse(t.encode('utf-8')), 'utf-8').split()
    longest = sorted(set(tokens), key=lambda x: len(x), reverse=True)
    if args.noascii:
        longest = [w for w in longest if not all(ord(c) < 256 for c in w)]

    ix = 0
    while True:
        for i, t in enumerate(longest[ix:ix+20]):
            print u'{0: >3}: {1} ({2})'.format(i + ix, t, len(t))
        userinput = raw_input(u'action (l|N|q)? ').strip()
        if userinput == u'l':
            ix += 20
            continue
        if userinput == u'q':
            loop = 'break'
            break
        if not re.match(r'^\d+$', userinput):
            print u'UNKNOWN ACTION'
            continue
        i = int(userinput)
        ix = int(i / 20) * 20
        t = longest[i]
        pending_words = {}
        print u'customizing for {0: >3}: {1} ({2})'.format(i, t, len(t))
        while True:
            userinput = uinput(u'action (e |N:N|d|n|v|q)? ')
            if userinput == u'n':
                break
            if userinput == u'v':
                loop = 'verify'
                break
            if userinput == u'q':
                loop = 'break'
                break
            if userinput == u'd':
                print u', '.join(sorted(user_words.keys()))
                continue
            if re.match(ur'^e [^\s,]', userinput):
                _, items = userinput.split(' ', 1)
                items = [item.strip() for item in items.split(',', 3)]
                items = (items + ['', '', ''])[:4]
                if raw_input(u'adding {0} (y|n)? '.format(items[0])).strip() != u'y':
                    continue
                word = items[0]
                word_props = map(lambda x: x if x else word, items[1:])
            elif re.match(ur'^\d+:\d+$', userinput):
                (start, end) = userinput.split(':')
                word = t[int(start):int(end)]
                if raw_input(u'adding {0} (y|n)? '.format(word)).strip() != u'y':
                    continue
                word_props = [word, word, word]
            else:
                print u'UNKNOWN ACTION'
                continue
            pending_words[word] = word_props
        if loop == 'break':
            break
        if loop == 'verify' and pending_words:
            for word in pending_words:
                if word not in user_words:
                    user_words[word] = [word, u'', u'', u'1', u'名詞', u'一般', u'*', u'*', u'*', u'*',
                                        word_props[0], word_props[1], word_props[2]]
            tagger = update_userdic()
            print u'verifying... {0}'.format(unicode(tagger.parse(t.encode('utf-8')), 'utf-8'))
            if raw_input(u'the result is okay (y|n)? ').strip() != u'y':
                for word in pending_words:
                    del user_words[word]
                tagger = update_userdic()
                print u'the change(s) discarded'
            break
    if loop == 'break':
        break



