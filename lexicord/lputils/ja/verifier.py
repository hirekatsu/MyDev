# -*- coding: utf-8 -*-
from __future__ import print_function
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
    _ = bsl.read(format='tmx', name=r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/sep.tmx',
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

    sample1 = u'''
次世代の脅威防止ソリューション
対象読者 CIO、CISO、IT 部門責任者
情報セキュリティ責任者が知るべき真のインテリジェント脅威防止ソリューションと現代のサイバー攻撃を阻止する方法

次世代の脅威防止ソリューション
情報セキュリティ責任者が知るべき真のインテリジェント脅威防止ソリューションと現代のサイバー攻撃を阻止する方法
1
概要
企業をサイバー脅威から保護することがますます困難になっています。
標的型攻撃によって機密データの漏えい、財務上の損失、評判の失墜などのリスクが生まれ、高度な攻撃の進化は加速する一方です。
今日の攻撃者は豊富な資金を持ち、国家の支援を受けています。
このような攻撃者は、検出を回避しながら防御を破って重要なデータを侵害する新たな手法を考案し、持続的に攻撃を行います。
攻撃者の狙いは、クレジットカード情報やNetﬂixアカウント情報を盗んで金銭的利益を得ることから、金融、政治、国家への攻撃へと移っています。
こうした目的を持った攻撃者は、電力網を停止させたり、ランサムウェアによって病院のシステムをオフラインにしたり、標的型攻撃で騙して政治に影響を与えたり、金融市場システムを不安定化させたりします。
増大し変化し続ける脅威に対抗するため、企業は1つか2つのテクノロジや機能だけを搭載した脅威防止ソリューションではなく、エンドツーエンドの保護を提供するインテリジェントな次世代脅威防止ソリューションを必要としています。
次世代脅威防止ソリューションとは一体何か
次世代脅威防止ソリューションとは何かをお客様とセキュリティ業界の皆様に理解していただけるように、シマンテックは先般、企業がソリューションで重視すべき事項を定義しました。
インテリジェントな次世代脅威防止ソリューションとは次の特長を備えるものです。
•高度な脅威とゼロデイ攻撃を事前にブロック
•世界中から収集した情報とビッグデータを活用してリアルタイムでサイバー脅威を防止
•高度な攻撃活動を検出し修復
•パフォーマンスに影響を与えずにすべての制御ポイントに最新の保護策を配備
これらの4つの機能は真の次世代脅威防止ソリューションの定義に不可欠な構成要素です。
以降のセクションでは、各構成要素をさらに詳しく説明します。
高度な脅威とゼロデイ攻撃を事前にブロック
多次元機械学習を用いて未知の攻撃を阻止
機械学習（ML）とは、大量のデータを自動で分析することで概念を学習するアルゴリズムです。
悪質なファイルやURLなどの新たな攻撃アーティファクトを検出するために、多くのセキュリティ企業がMLの「分類子」を使用しています。
たとえば、悪質なファイルの分類子を構築するために、正当なソフトウェアファイルと悪質なソフトウェアファイルを大量に集めて分析し、その振る舞い（プログラムがシステムディレクトリにあるファイルを削除しようとしたり、ファイルがセキュリティ設定を変更しようとするなど）を抽出する場合があります。
このトレーニングデータをMLシステムに投入することにより、MLシステムが正当なファイルと不正なファイルのそれぞれに関連する振る舞いの特徴を学習し、正当なファイルと不正なファイルを識別できるようになります。
このようなシステムの問題は、判定が振る舞いベースで行われるという点です。
振る舞いは完全に攻撃者の制御下にあるからです。
たとえば、攻撃者が脅威を修正して異なる振る舞いを示すようにするだけで、既存のML分類子では検出できなくなる可能性があります。
また、攻撃者が脅威のバイナリファイルのサイズを調整し、指示をいくつか入れ替えて新たな脅威を作れば、分類子はもう反応しません。
結局のところ、このように攻撃者が制御できる特徴（振る舞いやソフトウェアの指示）だけに依存しているMLシステムは、攻撃に対して極めて脆弱になります。
1-http://www.symantec.com/ja/jp/security_response/publications/threatreport.jsp

2
次世代の脅威防止ソリューション
情報セキュリティ責任者が知るべき真のインテリジェント脅威防止ソリューションと現代のサイバー攻撃を阻止する方法
シマンテックはセキュリティに対するまったく新しいアプローチとして、多次元機械学習を採用しました。
この新しいアプローチでは、従来の機能（前述の機能）と「集合知」を活用するクラウドアプローチを組み合わせ、単一のソフトウェアファイルやインターネット上のURLについて、シマンテックの数億人のお客様から収集した利用パターンを分析し、安全性を計算します。
ソフトウェアファイルやインターネット上のWebサイトとシマンテックのお客様との間で日常的に行われるやり取りは数兆件に及びます。
シマンテックのMLシステムはこのデータをリアルタイムで分析し、特定のユーザー群（パワーユーザー、初心者、企業、頻繁に攻撃を受けているユーザー、各地域のユーザーなど）に利用されているソフトウェアとWebサイトはどれか、同じユーザー群が利用を避けているソフトウェアとWebサイトはどれかを学習します。
このアプローチによって、完全に独立した方法でアーティファクトの安全性を評価することができます。
攻撃者が修正を加えることによって評価結果が変わることはほぼありません。
シマンテックの利用パターンベースのMLシステムは、特定のファイルについて、数千人のユーザーに利用されているのか、またはまったく利用されていないのかを把握してい
ます。
特定のファイルがパワーユーザーから避けられているかどうかも、頻繁に被害を受けているユーザーが高確率で利用しているかどうかも知っています。
このようにして、新たなファイルまたはURLの安全性についてのコンテキスト情報を大量に得られます。
シマンテックはこのユーザー利用パターンベースのMLアプローチを単独で活用するだけでなく、ソフトウェアファイル（またはURL）の振る舞いと構造に基づいて判定する従来のMLアプローチと組み合わせて活用しています。
これにより、ソフトウェアファイル（またはURL）の振る舞いと、シマンテックのお客様とのリアルタイムのやり取りの両方を判定に使用するMLシステムが実現されています。
この多次元アプローチによって攻撃への耐性が格段に高くなり、極めて敏感に検知するようになります（同時に誤検知も低減されます）。
クラウドコンポーネントを使わずエンドポイントベースのMLに完全に依存しているセキュリティ企業の問題点として他に挙げられるのは、攻撃者がエンドポイントでソフトウェアスタック全体を操作できる可能性があることです。
シマンテックの場合は、エンドポイントとクラウドの両方においてMLを利用します。そのため、攻撃者による侵害を許しません。
さらに、規模と速度も最適化されているため、さまざまな企業環境で効果を発揮します。
レピュテーション:Insight
シマンテックのInsightテクノロジは集合知と人工知能を活用して、高度な攻撃をほぼすべて（99.99%）ブロックします。
Insightはプログラム、実行元、IPアドレス、URL、デジタル署名者を1つ1つ追跡します。
さらに、広範なシマンテックのグローバルネットワーク全体にわたって、ダウンロードやプログラム起動のイベントを1つ残らず追跡しています。
3兆個にも及ぶこれらの要素によってシステムがトレーニングされるため、未知の脅威や未知のパターンを持つ脅威でさえもブロックできるのです。
Insightは関連性を大規模に追跡する唯一の人工知能であり、匹敵するテクノロジはありません。
属性:SAPE、Malheur
SAPEテクノロジでは、10億件以上の既知の脅威と正当なファイルからクラスタを生成します。
SAPEテクノロジの分類子は、このクラスタで発見されたものと一致する指標の組み合わせが新たなファイルにおいて見つかった場合に、悪質なファイルとして識別します。
そのため、既知のシグネチャが一切ない脅威でも、サイズ、構造、機械語の指示が既存の脅威クラスタに類似していれば、検出できる可能性があります。
SAPEは機械学習を利用して、クラスタを自動的に構築します。
数百の属性を用いて、多形態性の悪質なファイルを非常に低い誤検知率で検出します。

次世代の脅威防止ソリューション
情報セキュリティ責任者が知るべき真のインテリジェント脅威防止ソリューションと現代のサイバー攻撃を阻止する方法
3
振る舞い:SONAR
SONARと呼ばれる振る舞い監視テクノロジはリアルタイムの振る舞いに基づいて、脅威を検出します。
SONARは3つの異なる保護モードを利用します。
•シマンテックは、機械学習を利用して、数百万の正当なプログラムと悪質なプログラムの振る舞いプロファイルを分析します。
また、1400を超える分類子を利用して、悪質なソフトウェアクラスタに関連付けられた振る舞いの組み合わせを特定します。
このような振る舞いベースのルールによって、まったく新しいマルウェアでも、そのマルウェアの振る舞いに関する情報さえあれば、不審であると判定できます。
ソフトウェアファイルがまったく新しく、シグネチャを認識できない場合でも判定可能です。
•シマンテックのエンジニアは特定の振る舞いベースのルールを作成し、新しいマルウェアファミリーを即座に対処します。
たとえば、あるPOSマルウェアが必ず特定のセキュリティ設定を変更して特定のプロセスを起動しようとすることを発見した場合、シマンテックはこの振る舞いの組み合わせを識別するルールを作り、ブロックします。
•シマンテックのエンジニアは、正当なアプリケーションについても振る舞いベースのルールを作成して、侵害の対象になりやすい振
る舞いをロックまたはサンドボックス処理します。
たとえば、侵害されることの多いAcrobat Reader について、実行ファイルを作成してシステムの自動スタートアップに登録できないようにするルールを作成します。
Acrobat Readerなどのファイル閲覧ソフトは、本来システムに実行ファイルを作成するといった振る舞いを示さないはずなので、このようなシンプルなサンドボックス処理ルールによって、システムにある多くの脅威ベクトルを効果的に閉じることができます。
SONARはこれらの3つの方法を用いて、既知の攻撃、未知の攻撃、ゼロデイ攻撃を阻止します。
また、SONARは最新のうまく隠くれるNPT（Non-Process Threat）にも対処するよう設計されています。
NPTは、正当なアプリケーションに紛れ込むことによって、rootkitのような振る舞いを示すプログラムを隠したり、ウイルス対策をすり抜けたりしますが、このような脅威も追跡可能です。
クラスタリング:MutantX
マルウェアサンプルは1日あたり60万件から120万件という速さで増えています。
MutantXでは、これらのサンプルを正当なものと悪質なものとに正確かつ迅速に分類する新しい分散クラスタリングアルゴリズムが使用されています。
MutantXはシマンテックの新しい分散Hadoopコンピューティングプラットフォームでクラスタリングしているため、実質的には無制限に大量のサンプルをリアルタイムでクラスタリングできます。
サンプルとクラスタの数が制限されるのは、機械学習アルゴリズム専用のマシンノードの数によってのみです。
MutantXはクラスタリングする際に自動的に再トレーニングされるため、クラスタは常に最新状態が保たれ、正確です。
先進的な悪用防止機能と強化機能で未知の攻撃とゼロデイ攻撃を防止
システムロックダウン機能とアプリケーション制御機能によって、ポリシーベースの保護を簡単に作成して導入できます。
シマンテックは、トンネリングされたプロトコルを含む200を超えるプロトコルを解析できる能力と、レイヤー7トラフィック処理に対する深い理解を基に、エンドポイントにおける世界最高クラスの悪用防止機能を提供します。
システムロックダウン、アプリケーションおよびデバイスの制御
シマンテックの脅威防止ソリューションで提供されるアプリケーション制御機能とデバイス制御機能は、動的なポリシーベースの保護モデルを利用して不正な実行ファイルやデバイスがエンタープライズエンドポイントで実行されないようにブロックします。
シグネチャの更新や手間のかかる監視作業は必要ありません。
これにより、未知の脅威をプロアクティブにブロックするだけでなく、不要なアプリケーションを効果的に管理し、信頼できるアプリケーションとデバイスだけを確実に許可できます。
次世代ホストIPS:Vantage
Symantec Vantage IPSエンジンはネットワークベースの侵入に対する防御の最前線となります。
ディープパケットインスペクションを行い、送受信ネットワークストリームをそれぞれ解析することで、各フローのプロトコルと固有の脆弱性を把握し、異常や脆弱性の悪用を見つけます。
このため、このエンジンでは、不審なトラフィックがコンピュータのオペレーティングシステムやアプリケーションに到達する前に特定してブロックできます。
IPSは数百種類のプロトコルを把握して解読します。また、暗号化とネットワークトンネリングに対応できます。
Vantageは市場で最も先進的なホストベースのネットワーク侵入防止システムの1つです。
IPSは外部からの攻撃を検出してブロックするだけでなく、内部からコマンドアンドコントロールサーバーへの不正な送信トラフィックも検出できます。
これは極めて価値ある機能といえます。
Vantage IPSでは、高度な攻撃によってマシンが侵害され、他の保護レイヤーがすり抜けられてしまうような場合でも、トラフィックシグネチャに基づいてその脅威の存在を特定できます。
また、IPSは、ATP、ダウンロードインサイト、振る舞いベースの保護などの他の検出テクノロジが使用する、貴重な情報を収集するためにも使用されます。
攻撃者がVantageから逃れることは非常に困難です。
過去12カ月にわたって、Vantageは10億件を超える攻撃をブロックしました。
Vantageはゲートウェイで保護を行うNGFW（次世代ファイアウォール）よりも強力なエンドポイントネットワーク保護機能を提供します。
ブラウザ保護:Canary
シマンテックのブラウザ保護テクノロジは、各Webページがブラウザに読み込まれてレンダリングされる際に監視するため、不正なWebサイトがブラウザを悪用したり「サンドボックス」を回避したりしないようブロックできます。
これにより、Webベースの脅威がエンドポイントに侵入するのを防止します。
この保護層のメリットは、暗号化されていない不明瞭化されたトラフィックをブラウザで見えるとおりに把握できることです。
包括的なマルウェア対策ソリューションの一環として多層防御を導入
機械学習ベース、ネットワークベース、強化ベース、ポリシーベースの保護がすべて連携することによって、最適なエンドポイント保護を実現します。
シマンテックは99.99%の保護で満足してはいません。
シマンテックの目標は、攻撃パス全体にわたって優れたテクノロジを組み合わせた多層型のアプローチによってお客様に100%の保護を提供することです。
エンドポイント、ネットワーク、電子メールにわたって相関分析することでAPT攻撃を阻止
標的型攻撃や持続型攻撃を検出するためには、攻撃活動に対する幅広く深い理解が求められます。
電子メール、エンドポイント、ネットワークという複数の制御ポイントにわたるシマンテックのインテリジェンスが、脅威の検出、相関分析、優先順位付け、修復に役立ちます。
潜在的な脅威の進行状況を、仮想マシンと物理マシンでのデトネーションによって監視することで、従来のサンドボックスシステムを回避するように設計された脅威を検出できます。
詳細については、Symantec Advanced Threat Protection のページをご覧ください。
Symantec Synapse™ による相関分析
Synapse 相関分析テクノロジは、設置されているすべての制御ポイントから疑わしい活動を集計することで、危険にさらされていて早急な修復を要するシステムを迅速に特定し、こうしたシステムに優先順位を付けます。
脅威による機密データの流出を阻止
シマンテックのデータ漏えい防止（DLP）テクノロジによって、お客様は機密情報がある場所、機密情報の使用方法、保護方法を把握することができます。
シマンテックは、コンテンツ一致、非構造化フィンガープリント、構造化分類、ベクトル機械学習（データサンプルから機密情報とはどのようなものかを学習するテクノロジ）などの先進的な方法を複数用い、コンテンツが機密情報であるか判定します。
さらに、シマンテックの暗号化テクノロジによって機密データへの不正アクセスを強力に防止することで、DLPを補完しています。
シマンテックはさまざまな補完的な手法を利用して、コンテンツが機密情報であるかを判定しています。
•コンテンツ一致では、正規表現またはパターンとの一致を見つけます（たとえば、「クレジットカードのパターンがあればブロック」）。
•データ完全一致では、データベースにある機密データを直接特定します（たとえば、「顧客名とそれに関連する銀行口座番号の流出をブロック」）。
•インデックス文書一致では、「完全なファイルフィンガープリント」を適用して、非構造化データ（Microsoft Ofﬁce 文書や PDF ファイル、およびJPEG、CAD設計、マルチメディアファイルなどのバイナリファイル）の中にある機密情報を特定します。

次世代の脅威防止ソリューション
情報セキュリティ責任者が知るべき真のインテリジェント脅威防止ソリューションと現代のサイバー攻撃を阻止する方法
5
•ベクトル機械学習では、財務関連文書やソースコードといった機密文書タイプのレイアウトを自動的に学習して特定します。
•ファイルタイプ検出では、電子メール、グラフィック、カプセル化されたフォーマットなど、330種類以上のファイルタイプを認識します。
また、ほぼすべてのカスタムファイルタイプも認識できます。
世界中から収集した情報とビッグデータを活用してリアルタイムでサイバー脅威を防止
卓越した技能を誇る脅威研究の専門家
シマンテックの世界トップクラスの脅威研究者は、インテリジェンスフィードを継続的に分析することで新しい知見を得ており、脅威に対抗する最先端の革新的なセキュリティソリューションを開発しています。
シマンテックでは、1,000人を超えるセキュリティ専門家が世界中の9カ所にあるオペレーションセンターで業務に携わり、現場から集めた数十ペタバイトのインテリジェンスを調べて、新しい攻撃、新しい脅威ベクトルを発見するとともに、お客様のネットワークを監視しています。
このチームのメンバーのサイバーセキュリティに関する経験年数を合計すると、数千年に及びます。
多様な脅威に関するデータの分析
シマンテックは、さまざまな業界、地域、制御ポイント、ベクトル、ユーザーにわたって長期的に脅威を検出しているため、内容の濃い、深い知見が蓄積されています。
シマンテックの製品では、従来のように脅威の警告だけを収集するのではなく、世界中の数十億のWebサイト、ソフトウェアファイル、電子メールアドレス、IPアドレスの振る舞いと属性に関する遠隔測定データを収集しています。
このデータの規模と多様性は他に類を見ないものです。シマンテックはこのデータを集約して分析する能力を持っているため、攻撃を検出し、リスクを評価して軽減することが可能になり、情報保護をどの企業よりも適切に支援できます。
最新の脅威が用いる手法についての詳細な情報を入手
クラウドで管理されている高度に集約されたグローバルネットワークを活用して、最新の脅威が用いる手法についての詳細な情報を入手できます。
2億台を超えるセンサーで構成されたシマンテックのグローバルネットワークから、ソフトウェアの普及状況、特性、正常な振る舞いと不正な振る舞いに関する豊富な情報が提供されます。
実際のお客様の環境から収集された数兆個のデータポイントでMLアルゴリズムをトレーニングしているため、脅威が用いる新しい手法と回避策を常に発見し続けることが可能です。
Symantec Cynic™ - クラウドベースのサンドボックスおよびペイロードデトネーションサービス
Cynicは、高度な機械学習ベースの分析とシマンテックのグローバルインテリジェンスを組み合わせて活用し、最も検出の難しい継続的な脅威でさえも検出します。
また、Cynicによって、お客様はファイルの機能と実行時のすべてのアクションについて詳しく把握できるので、攻撃に関連するすべての要素を迅速に修復できます。
今日、高度な攻撃の28%は「仮想マシン認識型」です。
通常のサンドボックスシステムで実行しても、疑わしい振る舞いを見せることはありません。
これに対抗するため、Cynicは不審なファイルを物理ハードウェアでも実行し、従来のサンドボックステクノロジをすり抜けるこのような攻撃を検出します。
即座に保護
シマンテックのクラウドアルゴリズムは、ほとんどリアルタイムで更新されるため、すべてのエンドポイントを即座に保護します。
高度な攻撃活動を検出して修復
すべてのイベントに関する詳細なフォレンジックと修復機能によって標的型攻撃を素早く修復
今日の標的型攻撃では、脆弱性、ソーシャルエンジニアリング、フィッシングWebサイト、あるいはこれらを組み合わせた手法が用いられます。
いずれの手法でも、標的の企業に侵入するためにエンドポイントシステムが利用されます。
攻撃者は、企業のインフラに入り込むと、エンドポイントシステムを使用してネットワークを探索し、資格情報を盗み出してコマンドアンドコントロールサーバーに接続します。
企業の重要なシステムとデータを侵害するためです。

6
次世代の脅威防止ソリューション
情報セキュリティ責任者が知るべき真のインテリジェント脅威防止ソリューションと現代のサイバー攻撃を阻止する方法
企業に対する標的型攻撃の初期の徴候に気づき、脅威の影響をすべて取り除いて迅速に修復することが大切です。
シマンテックのエンドポイント、検出、および対応（EDR）テクノロジは一見すると別のものと思われるエンドポイントのイベントを結びつけて、攻撃の真の構造を明らかにします。
イベントデータを収集して、可視化、分析し、脅威を検出して修復します。
時間をさかのぼり、脅威の侵入方法やこれまでの進行状況を把握できます。
素早い修復
攻撃要素が悪質なものであると判定された時点で、お客様はすべてのエンドポイントから攻撃要素を即座に削除し、今後一切実行されないようにブロックできます。
また、攻撃に関わるすべての痕跡とその相互関係がグラフィカルに表示され、わかりやすく可視化されます。
グローバルインテリジェンスとローカルのコンテキスト情報を組み合わせて、迅速な攻撃の検出と優先順位付けを実現
世界最大規模のサイバー脅威インテリジェンスネットワークから収集したグローバルインテリジェンスと、エンドポイント、ネットワーク、電子メールから収集したお客様のローカルにあるコンテキスト情報とを組み合わせることで、検出を回避するように設計された攻撃も検出し、優先順位を付けます。
セキュリティアナリストは、脅威が企業に侵入した方法、脅威の影響を受けたコンピュータ、脅威によって新たに作成されたファイルやダウンロードされたファイルなど、エンドポイント攻撃の詳細を1カ所から確認できます。
また、企業内のすべてのエンドポイントを対象に、攻撃の痕跡を探すこともできます。
たとえば、「BAD.EXEというファイルのあるすべてのコンピュータ」や「レジストリキーXが存在し、その設定がYとなっており、Z.comというWebサイトに接続したことがあるすべてのコンピュータ」を一覧表示できます。
既存の Symantec Endpoint Protection 環境を活用
シマンテックの先進的なEDRソリューションでは、既存のSymantec Endpoint Protection への投資がより一層活用されます。
新しいエンドポイントエージェントの導入は不要です。
Symantec Endpoint Protection はエンドポイントで動作する単一のエージェントで、保護機能だけではなく検出機能と対応機能も提供します。
充実したインテリジェンスをエクスポート
この製品は、充実したインテリジェンスをサードパーティのセキュリティインシデント/イベント管理システム（SIEM）にエクスポートします。
また、シマンテック™マネージドセキュリティサービスで監視可能です。
シマンテックのEDRソリューションは、サードパーティ製のSIEM（Security Incident and Event Management System）にデータをエクスポートできます。
その内容は「ウイルスBAD.EXEが検出されました」のような曖昧なものではなく、「コンピュータAがWebサイトC.comからB.EXEというファイルをダウンロードしました」といった詳細なものです。
また、シマンテックのEDRソリューションはシマンテック™マネージドセキュリティサービスで監視可能です。
詳細については、『Advanced Threat Protection: Endpoint データシート』をご覧ください。
パフォーマンスに影響を与えずにすべての制御ポイントに最新の保護策を配備
あらゆる規模の企業のさまざまな種類のデバイスに配備可能
あらゆる環境に配備できます。
大企業でも小規模企業でも、分散したフランチャイズ方式を採用している場合でも、集中型の環境でも、さらには、高速なデジタルネットワークでも、低帯域幅のネットワークでも、ダークネットワークでも対応可能です。
あらゆる業界と政府機関に対応しており、プライベートクラウドやパブリッククラウド、それ以外の環境にも配備できます。
シマンテックのエンドポイントソリューションはPC、Mac、Linux、Android、およびiOSの幅広いデバイスをサポートしています。

次世代の脅威防止ソリューション
情報セキュリティ責任者が知るべき真のインテリジェント脅威防止ソリューションと現代のサイバー攻撃を阻止する方法
7
ネットワークの状況に関係なくハイパフォーマンスを維持
デバイスとネットワーク上でのパフォーマンスが最適化されており、運用に影響を与えないハイパフォーマンスな保護機能であらゆるプラットフォームを保護します。
そのため、スキャン時間、ブラウザ起動時間、マシン起動時間が短縮されます。
Passmark社のテストによると、SEPは業界で最も低負荷で高速なエンドポイント保護スイートです。
起動またはブラウジングでのレイテンシーがほぼ発生せず、スキャン活動によるメモリまたはCPUへの影響も最小限に抑えられていることが明らかになりました。
シマンテックは2億台を超えるエンドポイントに毎日新しいアルゴリズムとコードを提供し、60億を超えるファイルとWebサイトの安全性評価を行っています。
また、正当なプログラムがブロックされないように、自動化されたテクノロジと世界中から収集した情報が活用されています。
誤検知による中断を最小限に抑えて生産性を維持
シマンテックは誤検知の発生を防ぐためにはどんな苦労も惜しみません。
誤検知（FP）がセキュリティ業界の全ベンダーにとって懸案事項であることは明らかです。
しかし、多くのお客様にご利用いただいているシマンテックでは、誤検知による生産性低下の発生をゼロに近づけるため、はるかに高い水準を設定しています。
まとめ
革新的な考え方をすれば革新的な結果が得られます。
シマンテックは継続して技術革新に取り組んでおり、脅威防止、情報保護、サイバーセキュリティサービス、統合セキュリティ分析という4つの重要な柱に基づいてビジョンを構築しています。
現在、広範なセキュリティ遠隔測定データを収集して分析することでローカルとグローバルの脅威を特定し、その知見を確かな成果に変えることができる包括的なビッグデータ分析プラットフォームを開発中です。
また、シマンテックのビジョンの実現には、機械学習および深層学習テクノロジのさらなる進歩が欠かせません。
シマンテックの革新、製品、アプローチに対する独立機関のアナリストと研究者の評価
先般、独立系調査機関AV-TESTは Symantec Endpoint Protection が企業向けエンドポイントセキュリティに対する Best Protection 2015賞を獲得したと発表しました。
また、シマンテックはGartner社のマジッククアドラントで初回から毎回リーダー2（エンドポイント保護部門）に認定されています。
シマンテックは『2016 Gartner Magic Quadrant』 レポートの Data Loss Prevention、Managed Security Service Providers、および Endpoint Protection Platforms という 3 つの重要分野でリーダーに認定されました。
Symantec Advanced Threat Protection（SATP）は市場を席巻し、その保護機能は、第三者機関により実証されています。
Miercom は複数のATP ベンダー3について、APT（Advanced Persistent Threat）と AET（高度な回避技法）に対する防御能力のテストを実施しました。
他ベンダーの成績は著しく悪いものでした。
Cisco Systems 社は AET テストのわずか 5% しか検出できず、FireEye 社はまったく検出できませんでした。
シマンテックはAPTとAETの検出においていずれも100%という完璧な成績4を収めました。
これにより、エンドポイント、電子メール、ネットワークの保護を統合するというシマンテックの複数制御ポイントアプローチがATPに有効であることが実証されました。
また、SATP は Dennis Technology Labs 社が先頃実施したテストで検出精度 100% という最高ランクに格付けされ5、Palo Alto Networks
社、Cisco Systems 社、Fortinet 社を上回りました。
また、Dennis Technology Labs 社は Symantec Endpoint Protection に最高の AAA 評価を与えました。
シマンテックは Dennis 社のレポートで 14 四半期連続で最高評価を得ており、これを成し遂げているのはシマンテックだけです。
SEPとSATPを合わせて提出したことで、シマンテックは Dennis Technology Labs 社のテストにエンドポイント保護ソリューションと高度脅威防止ソリューションの両方を提供した唯一のベンダーとなり、脅威防止、検出、対応のニーズのあらゆる面に対応できる包括的かつ効果的な脅威防止ソリューションを提供する卓越した実力が実証されました。
2-http://www.symantec.com/connect/blogs/and-the-best-protection-award-2015-goes-to-symantec-endpoint-protection-by-avtest
3-http://miercom.com/symantec-advanced-threat-protection-2/
4-http://www.symantec.com/connect/blogs/symantec-advanced-threat-protection-outperforms-competitors-independent-third-party-tests
5-http://www.dennistechnologylabs.com/reports/s/a-m/2015/DTL_2015_Q4_Ent.1.0.pdf

8
次世代の脅威防止ソリューション
情報セキュリティ責任者が知るべき真のインテリジェント脅威防止ソリューションと現代のサイバー攻撃を阻止する方法
AV-ComparativesとMRG-Effitas社は先頃、1次元のテクノロジアプローチを採用している特定市場指向型の競合他社とシマンテックの革新的技術および保護能力を比較するために、Symantec Endpoint Protection と CylanceProtect について、実際の環境における詳細な比較を実施しました。
ただし、Cylance社はこのテストのためにソフトウェアを提供することに乗り気ではなかったようです。
結果は、「Symantec Endpoint Protection は実際のマルウェア攻撃を誤検知なしで100%ブロック」したのに対し、Cylance社の製品は有効性が92%に留まりました。
さらに顕著だったのは、SEPがCylanceProtectよりも45%多くの悪用を防止した点であり、SEPは全体の90%を保護したのに対し、CylanceProtectは63%でした。
AV-ComparitivesとMRG-Efﬁtas社のテストから、シマンテックの事前対応型の実行前検出機能と防止能力が卓越していることは明白です。
全体の有効性が著しく高かったことに加え、SEPはCylanceProtectよりも3倍多く悪用を防止しました。
AV-ComparativesとMRG-Efﬁtas社は次のように述べています。
「この第三者評価で実際の脅威と悪用に対する防止機能を比較したところ、Cylance社の提供する保護機能は、シマンテックの保護機能に比べて、明らかに劣っていました。」AV-ComparativesとMRG-Efﬁtas社によるこれらのテスト結果から、シマンテックのラボにて独自に行っている予備テストが有効であることがわかります。
この予備テストではCylance社とその製品の有効性に関する広告について同様の懸念を明らかにしていました。
AV-ComparativesとMRG-Effitas社は、特定市場指向型の新規参入企業に関して興味深い考察を行い、こうした企業は一般に、第三者のラボでのテストについて次のような姿勢をとると述べました。
「次世代を謳う新製品の多くで見られる傾向ですが、実証されていないマーケティング広告によってユーザーに製品を売り込み続けるために、テストを受けることを避けているように見えます。」
このような成果によって、シマンテックが引き続きサイバーセキュリティ分野のリーダーであることが実証され、シマンテックの継続的な革新によって業界が発展していることが示されました。称賛を得たことは光栄ではあるものの、シマンテックはこれからもお客様のお役に立てるよう、「真の次世代脅威防止ソリューションの定義と提供」に力を注ぐ所存です。
シマンテックの次世代脅威防止ソリューションについての詳細は、こちらをご覧ください。
6-http://www.av-comparatives.org/wp-content/uploads/2016/02/avc_mrg_prot_2016_02_24_cyl_sym_en.pdf
7-https://www.mrg-efﬁtas.com/wp-content/uploads/2016/02/avc_mrg_prot_2016_02_24_cyl_sym_en.pdf
8-http://www.symantec.com/connect/blogs/cylanceprotect-symantec-labs-analysis
Copyright
© 2016 Symantec Corporation. All rights reserved. Symantec、
Symantec ロゴ、チェックマークロゴは、
Symantec Corporation または関連会社の米国およびその他の国における商標または登録商標です。
その他の会社名、製品名は各社の商標または登録商標です。
株式会社シマンテック
〒１０７-００５２ 東京都港区赤坂１-１１-４４ 赤坂インターシティ
www.symantec.com/jp
お問い合わせ
E1603DS0-IN-21364292
    '''
    sample1 = sample1.split(u'\n')
    print(sample1[0])

    mtagger = MeCab.Tagger('-u /Users/kiyoshi_izumi/Desktop/DATA/DEV/MyGitHub/MyDev/lexicord/mydic.dic')
    verifier = JapaneseTermVerifier(mtagger)
    for t in sample1:
        verifier.feed_sent(t)
    verifier.print_katakana_inconsistency()
    verifier.print_homonym()
    verifier.print_scarce()
    verifier.print_aaa()

    # verifier.model1(t for (s, t) in bsl)
    # bsl2 = BilingualSegmentList()
    # _ = bsl2.read(format='tmx', name=r'/Users/kiyoshi_izumi/Desktop/DATA/PROJ/MT/160427_nltk/samples/dlp.tmx',
    #               encoding='utf-16', verbose=True, metatextparser=htmldecode)
    # for (s, t) in bsl2:
    #     verifier.verify1(t)





