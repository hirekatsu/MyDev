# -*- coding: utf-8 -*-
from __future__ import print_function
from local_settings import myenv, text1
import MeCab
import nltk
import re
from collections import defaultdict
from lputils.ja.katakana import Katakana


class JapaneseTermVerifier(object):
    def __init__(self, mecab_tagger):
        self._tagger = mecab_tagger
        self._katakana = Katakana()
        self._homonym = nltk.ConditionalFreqDist()
        self._freqdist = nltk.FreqDist()
        self._aaa = nltk.ConditionalFreqDist()

        self._sentences = []
        self._examples = {}

    def _tokenize(self, sentence):
        tokens = []
        encoded_sent = sentence.encode('utf-8')
        node = self._tagger.parseToNode(encoded_sent)
        node = node.next
        while node and node.surface:
            tokens.append((node.surface.decode('utf-8'),
                           (node.feature.decode('utf-8').split(u',') + [u'', u'', u''])[:8],
                           node.cost))
            node = node.next
        return tokens

    def feed_sent(self, sentence):
        self._sentences.append(sentence)
        tokens = self._tokenize(sentence)
        for (surface, feature, _) in tokens:
            self._examples[surface] = len(self._sentences) - 1
            # katakana
            self._katakana.add_to_dict(surface)
            # homonym
            if feature[7]:
                self._homonym[feature[7]][surface] += 1
            # non-ascii word for freq
            if all(ord(c) >= 256 for c in surface):
                self._freqdist[surface] += 1

        for i in range(len(tokens)-1):
            self._aaa[(tokens[i][0], tokens[i][1][0]+u','+tokens[i][1][1])][tokens[i+1][1][0]+u','+tokens[i+1][1][1]] += 1


        #if 10000 < len(self._sentences) < 10020:
        if u'取り込め' in sentence:
            print(u'----------')
            print(u' '.join(s for (s, f, c) in tokens))
            for (s, f, c) in tokens:
                print(s, u'->', end=u' ')
                print(u', '.join(f), end=u' -> ')
                print(c)

        return [surface for (surface, feature, _) in tokens]

    def model1(self, sents):
        cfd = nltk.ConditionalFreqDist()
        for sent in sents:
            tokens = self._tokenize(sent) + [(u'', [u'',u'',u'',u'',u'',u'',u'',u''], 0)]
            for i in range(len(tokens)-1):
                cfd[(tokens[i][0], tokens[i][1][0]+u','+tokens[i][1][1])][tokens[i+1][1][0]+u','+tokens[i+1][1][1]] += 1
        self._model1 = defaultdict(list)
        for (k, fd) in cfd.items():
            for (pos, f) in fd.items():
                if f >= 5:
                    self._model1[k].append(pos)

    def verify1(self, sent):
        tokens = self._tokenize(sent) + [(u'', [u'',u'',u'',u'',u'',u'',u'',u''], 0)]
        for i in range(len(tokens)-1):
            k = (tokens[i][0], tokens[i][1][0]+u','+tokens[i][1][1], )
            n = tokens[i+1][1][0]+u','+tokens[i+1][1][1]
            if k in self._model1:
                if n not in self._model1[k]:
                    print(u'-' * 30)
                    print(u' '.join(s for (s, f, c) in tokens[:i]), end=u' ')
                    print(u'[', tokens[i][0], u']', end=u' ')
                    print(u' '.join(s for (s, f, c) in tokens[i+1:]))
                    print(u'EXPECT:', u','.join(k), u'->', u'/'.join(self._model1[k]))
                    print(u'ACTUAL:', u','.join(k), u'->', n)


    def print_aaa(self):
        for ((w, p), fd) in self._aaa.items():
            if not p.startswith(u'名詞,') and len(fd) <= 2:
                if len(fd) == 1:
                    print(u'*', end='')
                print(u'{0} | {1} -->'.format(w, p), end=' ')
                for (n, f) in fd.items():
                    print(u'{0} ({1})'.format(n, f), end=' ')
                print()

    def print_katakana_inconsistency(self):
        print(u'KATAKANA ' + u'-' * 50)
        for kl in self._katakana.inconsistency():
            print(u'----------')
            for (w, f) in kl:
                print(u'{0} ({1})'.format(w, f))
                print(u'    {0}'.format(self._sentences[self._examples[w]]))

    def print_homonym(self):
        print(u'HOMONYM ' + u'-' * 50)
        for (yomi, fd) in sorted(self._homonym.items(), key=lambda x: x[0]):
            if len(fd) > 1:
                print(u'[{0}]:'.format(yomi))
                for (w, f) in sorted(fd.items(), reverse=True, key=lambda x: x[1]):
                    print(u'  {0} ({1})'.format(w, f))
                    print(u'    {0}'.format(self._sentences[self._examples[w]]))

    def print_scarce(self):
        print(u'SCARCE WORD ' + u'-' * 50)
        for (w, f) in sorted(self._freqdist.items(), key=lambda x: x[0]):
            if f == 1:
                print(w)
                print(u'    {0}'.format(self._sentences[self._examples[w]]))


if __name__ == '__main__':
    import HTMLParser
    from lputils.segmentlist import BilingualSegmentList

    html_parser = HTMLParser.HTMLParser()


    def htmldecode(text):
        text = re.sub(r'</?[A-Z].*?>', '', text, flags=re.I + re.U)
        text = html_parser.unescape(text)
        return text

    bsl = BilingualSegmentList()
    _ = bsl.read(format='tmx', name=myenv.tmxS,
                 encoding='utf-16', verbose=True, metatextparser=htmldecode)

    bsl.replace(u'\u2028', u' ')
    bsl.replace(u'\u3000', u' ')
    bsl.replace(u'\u00A0', u' ')
    bsl.replace(u'\uFF43', u' ビット')
    bsl.replace(u'\uFF47', u'g')
    bsl.replace(u'\uFF10', u'0')
    bsl.replace(u'\uFF12', u'2')
    bsl.replace(u'\uFF15', u'5')
    bsl.replace(u'ＴＩＲ', u'TIR')
    bsl.replace(u'\uFF61', u'。', where='target')

    bsl.replace(u'トライプラリ', u'とライブラリ', where='target')
    bsl.replace(u'アーカイブスタスク', u'アーカイブタスク', where='target')
    bsl.replace(u'ストーレジ', u'ストレージ', where='target')
    bsl.replace(u'コントロールパネ］', u'コントロールパネル］', where='target')
    bsl.replace(u'ディレクアレイ', u'ディスクアレイ', where='target')
    bsl.replace(u'ハイバーバイザ', u'ハイパーバイザ', where='target')
    bsl.replace(u'クライアンで', u'クライアントで', where='target')
    bsl.replace(u'TCP フージョン', u'TCP フュージョン', where='target')
    bsl.replace(u'ディ スクベース', u'ディスクベース', where='target')
    bsl.replace(u'コン ピュータ', u'コンピュータ', where='target')
    bsl.replace(u'フェー ズ', u'フェーズ', where='target')
    bsl.replace(u'バックアアップ', u'バックアップ', where='target')
    bsl.replace(u'ガーべジ', u'ガーベジ', where='target')
    bsl.replace(u'べース', u'ベース', where='target')
    bsl.replace(u'ボールト', u'ボルト', where='target')
    bsl.replace(u'復号化鍵', u'復号鍵', where='target')
    bsl.replace(u'複合に失敗', u'復号', where='target')
    bsl.replace(u'良く寄せられる', u'よく寄せられる', where='target')

    bsl.replace(u'フェイルオーバー', u'フェールオーバー', where='target')
    bsl.replace(u'ネイティブ', u'ネーティブ', where='target')
    bsl.replace(u'シャドー', u'シャドウ', where='target')
    bsl.replace(u'ウインドウ', u'ウィンドウ', where='target')
    bsl.replace(u'クォータ', u'クオータ', where='target')
    bsl.replace(u'インストーラー', u'インストーラ', where='target')
    bsl.replace(u'インタフェース', u'インターフェース', where='target')
    bsl.replace(u'エントリー', u'エントリ', where='target')
    bsl.replace(u'コンピューター', u'コンピュータ', where='target')
    bsl.replace(u'サードパーティー', u'サードパーティ', where='target')
    bsl.replace(u'セキュリティー', u'セキュリティ', where='target')
    bsl.replace(u'テクノロジー', u'テクノロジ', where='target')
    bsl.replace(u'プリンター', u'プリンタ', where='target')
    bsl.replace(u'ビューアー', u'ビューア', where='target')
    bsl.replace(u'ブロッカー', u'ブロッカ', where='target')
    bsl.replace(u'メモリー', u'メモリ', where='target')
    bsl.replace(u'ワーカスレッド', u'ワーカースレッド', where='target')
    bsl.replace_re(ur'カスタマ(?!ー)', u'カスタマー', where='target')
    bsl.replace_re(ur'クエリ(?!ー)', u'クエリー', where='target')
    bsl.replace_re(ur'サーバ(?!ー)', u'サーバー', where='target')
    bsl.replace_re(ur'トポロジ(?!ー)', u'トポロジー', where='target')
    bsl.replace_re(ur'ファイバ(?!ー)', u'ファイバー', where='target')
    bsl.replace_re(ur'ヘッダ(?!ー)', u'ヘッダー', where='target')
    bsl.replace_re(ur'ベンダ(?!ー)', u'ベンダー', where='target')
    bsl.replace_re(ur'マスタ(?!ー)', u'マスター', where='target')
    bsl.replace_re(ur'メンバ(?!ー)', u'メンバー', where='target')
    bsl.replace_re(ur'ユーザ(?!ー)', u'ユーザー', where='target')
    bsl.replace_re(ur'ルータ(?!ー)', u'ルーター', where='target')

    bsl.replace(u'ヶ月', u'カ月', where='target')
    bsl.replace(u'か月', u'カ月', where='target')
    bsl.replace(u'箇所', u'カ所', where='target')

    bsl.replace(u'稼動', u'稼働', where='target')
    bsl.replace(u'疑似', u'擬似', where='target')
    bsl.replace(u'切り換え', u'切り替え', where='target')
    bsl.replace(u'遵守', u'順守', where='target')
    bsl.replace(u'お奨めします', u'お勧めします', where='target')

    bsl.replace(u'開放', u'解放', where='target')
    bsl.replace(u'越えて', u'超えて', where='target')
    bsl.replace(u'越える', u'超える', where='target')
    bsl.replace(u'平分で', u'平文で', where='target')

    bsl.replace(u'起こりえる', u'起こりうる', where='target')

    bsl.replace(u'曖昧', u'あいまい', where='target')
    bsl.replace(u'例をあげます', u'例を挙げます', where='target')
    bsl.replace(u'分当たりで', u'分あたりで', where='target')
    bsl.replace(u'あてはまる', u'当てはまる', where='target')
    bsl.replace(u'余りにも', u'あまりにも', where='target')
    bsl.replace(u'いえません', u'言えません', where='target')
    bsl.replace(u'いっさい', u'一切', where='target')
    bsl.replace(u'一旦', u'いったん', where='target')
    bsl.replace(u'隠ぺい', u'隠蔽', where='target')
    # bsl.replace(u'行なう', u'行う', where='target')
    bsl.replace(u' 及び ', u' および ', where='target')
    bsl.replace(u'およぼさ', u'及ぼさ', where='target')
    bsl.replace(u'終り', u'終わり', where='target')
    bsl.replace(u'に関わらず', u'にかかわらず', where='target')
    bsl.replace(u'関わりなく', u'かかわりなく', where='target')
    bsl.replace(u'関わる', u'かかわる', where='target')
    bsl.replace(u'書きとめ', u'書き留め', where='target')
    bsl.replace(u'構いません', u'かまいません', where='target')
    bsl.replace(u'かわりに', u'代わりに', where='target')
    bsl.replace(u'下さい。', u'ください。', where='target')
    bsl.replace(u'どの位', u'どのくらい', where='target')
    bsl.replace(u'実行した事が', u'実行したことが', where='target')
    bsl.replace(u'種類毎', u'種類ごと', where='target')
    bsl.replace(u'さかのぼっ', u'遡っ', where='target')
    bsl.replace(u'さかのぼる', u'遡る', where='target')
    bsl.replace(u'様々な', u'さまざまな', where='target')
    bsl.replace(u'、更に', u'、さらに', where='target')
    bsl.replace(u'仕組み', u'しくみ', where='target')
    bsl.replace(u'仕組', u'しくみ', where='target')
    bsl.replace(u'にしたがって', u'に従って', where='target')
    bsl.replace(u'従って 1 つの', u'したがって 1 つの', where='target')
    bsl.replace(u'既に', u'すでに', where='target')
    bsl.replace(u'素早く', u'すばやく', where='target')
    bsl.replace(u'全ての', u'すべての', where='target')
    bsl.replace(u'尋ねる', u'たずねる', where='target')
    bsl.replace(u'直ちに', u'ただちに', where='target')
    bsl.replace(u'例えば', u'たとえば', where='target')
    bsl.replace(u'次の通り', u'次のとおり', where='target')
    bsl.replace(u'ともなう', u'伴う', where='target')
    bsl.replace(u'接続し直し', u'接続しなおし', where='target')
    bsl.replace(u'なにもアップ', u'何もアップ', where='target')
    bsl.replace(u'初めてインストール', u'はじめてインストール', where='target')
    bsl.replace(u'初めて Oracle を', u'はじめて Oracle を', where='target')
    bsl.replace(u'外し', u'はずし', where='target')
    bsl.replace(u'外す', u'はずす', where='target')
    bsl.replace(u'ひそかに', u'密かに', where='target')
    # bsl.replace(u'ほうが', u'方が', where='target')
    bsl.replace(u'大きいほう', u'大きい方', where='target')
    bsl.replace(u'全く判読', u'まったく判読', where='target')
    bsl.replace(u'全く新しい', u'まったく新しい', where='target')
    bsl.replace(u'みなされ', u'見なされ', where='target')
    bsl.replace(u'みなし、', u'見なします', where='target')
    bsl.replace(u'みなします', u'見なします', where='target')
    bsl.replace(u'みなすこと', u'見なすこと', where='target')
    bsl.replace(u'とみなす', u'と見なす', where='target')
    bsl.replace(u'結びつける', u'結び付ける', where='target')
    bsl.replace(u'もっとも厳格', u'最も厳格', where='target')
    bsl.replace(u'をもつ厳密な', u'を持つ厳密な', where='target')
    bsl.replace(u'もっともよく使う', u'最もよく使う', where='target')
    bsl.replace(u'もともと', u'元々', where='target')
    bsl.replace(u'分からない', u'わからない', where='target')

    bsl.replace(u'受入れ', u'受け入れ', where='target')
    bsl.replace(u'書込み', u'書き込み', where='target')
    bsl.replace(u'書き込と', u'書き込みと', where='target')
    bsl.replace(u'切替える', u'切り替える', where='target')
    bsl.replace(u'支払済', u'支払い済', where='target')
    bsl.replace_re(ur'手続(?!き)', u'手続き', where='target')
    bsl.replace(u'問合せ', u'問い合わせ', where='target')
    bsl.replace(u'問い合せ', u'問い合わせ', where='target')
    bsl.replace(u'取入れ', u'取り入れ', where='target')
    bsl.replace(u'取消し', u'取り消し', where='target')
    bsl.replace(u'取消', u'取り消し', where='target')
    bsl.replace(u'取込み', u'取り込み', where='target')
    bsl.replace(u'取出し', u'取り出し', where='target')
    bsl.replace(u'取付け', u'取り付け', where='target')
    bsl.replace(u'巻戻し', u'巻き戻し', where='target')
    bsl.replace(u'読み込ために', u'読み込むために', where='target')
    bsl.replace(u'読取る', u'読み取る', where='target')
    bsl.replace(u'割当て', u'割り当て', where='target')

    bsl.prune_re(ur'[\u0081\u00BB\u00FB\u2022\u25BC]')
    bsl.prune(u'ＭＳ Ｐゴシック', where='target')
    bsl.trim()
    bsl.prune_re(ur'\\tCtrl\+[0-9A-Z]$', where='target')
    bsl.prune_re(ur'\([0-9A-Z]\)(\.\.\.)?$', where='target')
    bsl.prune_re(ur'\|[0-9A-Z]\|?$', where='source')
    bsl.prune_re(ur'^Usage:', where='source', flags=re.I)
    bsl.prune_re(ur'\\n$', where='source')
    bsl.prune_re(ur'\\n\\n', where='source')
    bsl.prune_re(ur'^IdxYomi=', where='source')
    bsl.prune(u'abcdefghijklmnopqrstuvwxyz', where='target')

    bsl.trim()
    bsl.empty(prune=True)
    bsl.duplicate(where='both', uniq=True)

    sample1 = text1.split(u'\n')
    print(sample1[0])

    mtagger = MeCab.Tagger('-u %s' % myenv.projfile('mydic.dic'))
    verifier = JapaneseTermVerifier(mtagger)
    for t in sample1:
        verifier.feed_sent(t)
    verifier.print_katakana_inconsistency()
    verifier.print_homonym()
    verifier.print_scarce()
    verifier.print_aaa()

    # verifier.model1(t for (s, t) in bsl)
    # bsl2 = BilingualSegmentList()
    # _ = bsl2.read(format='tmx', name=myenv.tmxD, encoding='utf-16', verbose=True, metatextparser=htmldecode)
    # for (s, t) in bsl2:
    #     verifier.verify1(t)




