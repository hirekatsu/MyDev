# -*- coding: utf-8 -*-
from __future__ import print_function
import re
from collections import defaultdict

class Katakana(object):
    """

    """

    # static variables
    chars_range = u'\u30A1-\u30FA\u30FC\u31F0-\u31FF'
    chars_a = u'ァアヵカガサザタダナハバパマャヤラワ'
    chars_i = u'ィイキギシジチヂニヒビピミリヰ'
    chars_u = u'ゥウクグスズッツヅヌフブプムュユル'
    chars_e = u'ェエヶケゲセゼテデネヘベペメレヱ'
    chars_o = u'ォオコゴソゾトドノホボポモョヨロヲ'
    chars_small = u'ァィゥェォヵヶッャュョ'
    re_obj = re.compile(ur'[%s]+' % chars_range)

    def __init__(self):
        self._dict = defaultdict(lambda: defaultdict(int))
        self._most = dict()

    def train(self, sents):
        self._dict = self._build_dict(sents)
        self._most = {k: sorted(self._dict[k].items(), reverse=True, key=lambda x: x[1])[0][0] for k in self._dict}
        return self

    def add_to_dict(self, token):
        for word in Katakana.re_obj.findall(token):
            key = Katakana._normalize(word)
            self._dict[key][word] += 1
            self._most[key] = sorted(self._dict[key].items(), reverse=True, key=lambda x: x[1])[0][0]

    def inconsistency(self):
        return [sorted(self._dict[k].items(), reverse=True, key=lambda x: x[1]) for k in sorted(self._dict) if len(self._dict[k]) > 1]

    def notational(self, sents, use_most_frequent=False):
        breaches = dict()
        for sent in sents:
            for w in self.notational_sent(sent, use_most_frequent=use_most_frequent):
                breaches[w] = 1
        return sorted(breaches)

    def notational_sent(self, sent, use_most_frequent=False):
        assert isinstance(sent, basestring) or hasattr(sent, '__iter__'), 'Unexpected type of sentence'
        breaches = dict()
        tokens = sent.split() if isinstance(sent, basestring) else sent
        for token in tokens:
            for word in Katakana.re_obj.findall(token):
                key = Katakana._normalize(word)
                if key in self._dict:
                    if word not in self._dict[key]:
                        breaches[word] = 1
                    elif use_most_frequent:
                        if word != self._most[key]:
                            breaches[word] = 1
        return sorted(breaches)

    @staticmethod
    def impossible(sents):
        breaches = dict()
        for sent in sents:
            for w in Katakana.impossible_sent(sent):
                breaches[w] = 1
        return sorted(breaches)

    @staticmethod
    def impossible_sent(sent):
        breaches = dict()
        assert isinstance(sent, basestring) or hasattr(sent, '__iter__'), 'Unexpected type in list of sentences'
        tokens = sent.split() if isinstance(sent, basestring) else sent
        for token in tokens:
            for word in Katakana.re_obj.findall(token):
                if re.match(ur'^[%sー]' % Katakana.chars_small, word):
                    breaches[word] = 1
                elif any(p in word for p in (u'ーー', u'ッー')):
                    breaches[word] = 1
        return sorted(breaches)

    @staticmethod
    def _build_dict(sents):
        kdict = defaultdict(lambda: defaultdict(int))
        for sent in sents:
            assert isinstance(sent, basestring) or hasattr(sent, '__iter__'), 'Unexpected type in list of sentences'
            tokens = sent.split() if isinstance(sent, basestring) else sent
            for token in tokens:
                for word in Katakana.re_obj.findall(token):
                    kdict[Katakana._normalize(word)][word] += 1
        return kdict

    @staticmethod
    def _normalize(text):
        t = text
        t = re.sub(ur'ウ?ヰ', u'Ｗイ', t)
        t = re.sub(ur'ウ?ヱ', u'Ｗエ', t)
        # ウイルス/ウィルス、ウオッカ/ウォッカ
        t = re.sub(ur'(ウア|ウァ)', u'Ｗア', t)
        t = re.sub(ur'(ウイ|ウィ)', u'Ｗイ', t)
        t = re.sub(ur'(ウウ|ウゥ)', u'Ｗウ', t)
        t = re.sub(ur'(ウエ|ウェ)', u'Ｗエ', t)
        t = re.sub(ur'(ウオ|ウォ)', u'Ｗオ', t)
        # スマートホン/スマートフォン
        t = re.sub(ur'(ハ|フア|ファ)', u'Ｆア', t)
        t = re.sub(ur'(ヒ|フイ|フィ)', u'Ｆイ', t)
        t = re.sub(ur'(ヘ|フエ|フェ)', u'Ｆエ', t)
        t = re.sub(ur'(ホ|フオ|フォ)', u'Ｆオ', t)
        t = re.sub(ur'(フ|フウ|フゥ)', u'Ｆウ', t)
        # バイオリン/ヴァイオリン、ボイス/ヴォイス
        t = re.sub(ur'(バ|ヴァ)', u'Ｂア', t)
        t = re.sub(ur'(ビ|ヴィ)', u'Ｂイ', t)
        t = re.sub(ur'(ブ|ヴゥ)', u'Ｂウ', t)
        t = re.sub(ur'(ベ|ヴェ)', u'Ｂエ', t)
        t = re.sub(ur'(ボ|ヴォ)', u'Ｂオ', t)
        # クオリティ/クォリティ
        t = re.sub(ur'(クア|クァ)', u'Ｑア', t)
        t = re.sub(ur'(クイ|クィ)', u'Ｑイ', t)
        t = re.sub(ur'(クウ|クゥ)', u'Ｑウ', t)
        t = re.sub(ur'(クエ|クェ)', u'Ｑエ', t)
        t = re.sub(ur'(クオ|クォ)', u'Ｑオ', t)
        # イニシアチブ/イニシアティブ
        t = re.sub(ur'(チ|ティ)', u'Ｔイ', t)
        t = re.sub(ur'(ヂ|ディ)', u'Ｄイ', t)
        # サプライヤ/サプライア, リニヤ/リニア
        t = re.sub(ur'(?<=[%s])[アヤ]' % Katakana.chars_i, u'Ｉア', t)
        # プリンター/プリンタァ/プリンタア > プリンタ〜, ダージリン/ダアジリン/ダァジリン > ダ〜ジリン
        t = re.sub(ur'(?<=[%s])[ーアァ]' % Katakana.chars_a, u'〜', t)
        # プリンタ > プリンタ〜, ハッカソン > ハッカ〜ソン, add to all possible ア except ones followed by a small KATAKANA
        t = re.sub(ur'(?<=[%s])(?![%s〜])' % (Katakana.chars_a, Katakana.chars_small), u'〜', t)
        # レート/レイト/レィト/レエト/レェト > レ〜ト
        t = re.sub(ur'(?<=[%s])[ーイィエェ]' % Katakana.chars_e, u'〜', t)
        # エコロジー/エコロジィ/エコロジイ > エコロジ〜
        t = re.sub(ur'(?<=[%s])[ーイィ]' % Katakana.chars_i, ur'〜', t)
        # エコロジ > エコロジ〜, add to all possible イ but ミュージック remains as is
        t = re.sub(ur'(?<=[%s])(?![%s〜])' % (Katakana.chars_i, Katakana.chars_small), ur'〜', t)
        # ビュー/ビュウ/ビュゥ > ビュ〜
        t = re.sub(ur'(?<=[%s])[ーウゥ]' % Katakana.chars_u, u'〜', t)
        # シャドー/シャドウ/シャドゥ/シャドオ/シャドォ > シャド〜
        t = re.sub(ur'(?<=[%s])[ーウゥオォ]' % Katakana.chars_o, u'〜', t)
        t = t.replace(u'〜ー', u'〜')

        # TODO デ/ジ/ディ, レ/リ, カーラー/カラー, フォルダ/ホルダー, ホーム/フォーム,
        return t


if __name__ == '__main__':
    sentences1 = [
        u'ウイスキー と ウヰスキー',
        u'ウェールズ と ヱールズ',
        u'スマートフォン と スマートホン 、 テレフォン と テレホン',
        u'バイオリン と ヴァイオリン 、 ボイス と ヴォイス',
        u'ウイルス と ウィルス',
        u'クオリティー と クォリティー',
        u'イニシアチブ と イニシアティブ',
        u'リアカー と リヤカー',
        u'プリンター と プリンタ と プリンタァ と プリンタア 、 ユーザー と ユーザ',
        u'ネーティブ と ネイティブ と ネィティブ と ネエティブ と ネェティブ 、 エージェント と エイジェント',
        u'トポロジ と トポロジー 、 フレンドリ と フレンドリー',
        u'キュー と キュウ',
        u'シャドー と シャドウ と シャドゥ と シャドオ と シャドォ',
        u'ユーザー フレンドリー な プリンター を 使用 する 。'
    ]

    sentences2 = [
        u'ユーザ フレンドリ な プリンタ を 使用 する 。',
        u'エコロジー と エコロジ',
        u'データべース ェックボックス'
    ]

    kata = Katakana()
    print(u'-' * 50)
    kata.train(sentences1)
    for norm in kata._dict:
        print(norm + u':')
        print(u'  ', end=u'')
        for (w, f) in kata._dict[norm].items():
            print(u'{0} ({1})'.format(w, f), end=u', ')
        print()
    print(u'-' * 50)
    for klist in kata.inconsistency():
        for w, f in klist:
            print(u'{0} ({1})'.format(w, f), end=u', ')
        print()
    print(u'-' * 50)
    for breach in kata.notational_sent(u'ユーザー と ユーザ'):
        print(breach)
    print(u'-' * 50)
    for breach in kata.notational_sent(u'ユーザー と ユーザ', use_most_frequent=True):
        print(breach)
    print(u'-' * 50)
    for breach in kata.notational(sentences2, use_most_frequent=True):
        print(breach, end=u', ')
    print()
    print(u'-' * 50)
    for breach in kata.impossible(sentences2):
        print(breach, end=u', ')




