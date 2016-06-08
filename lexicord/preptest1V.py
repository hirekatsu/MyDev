# -*- coding: utf-8 -*-
from local_settings import myenv
from lputils.seglist import BiSegList
from lputils.unicodeprint import unicodeprint as up

bsl = BiSegList()
_ = bsl.read(format='tmx', name=myenv.tmxV, encoding='utf-8', verbose=True)
print len(bsl)

bsl.trim()
bsl.rereplace(r'{\d+}', '')
bsl.prune(bsl.research(u'[\u203B\u25CE\u2605\u2666\u3010\u3011]'))
bsl.prune(bsl.research(ur'^(%d{|advanced local-auth {|configure (>|Configure|interface|spm ip|spm {)|local-db|date {|Enforcer|verify)', where='target'))
bsl.prune(bsl.research(ur'^help ', where='source'))
bsl.prune(bsl.research(ur'^\|', where='source'))
bsl.prune(bsl.research(ur' \| .*? \| ', where='source'))
bsl.prune(bsl.research(ur'\.\.\.$', where='target'))
bsl.prune(bsl.research(ur'^Allow LiveUpdate to run on a schedule', where='target'))
bsl.prune(bsl.research(ur'^spm ip 192', where='target'))
bsl.prune(bsl.research(ur'^a newer version of the software is available', where='target'))
bsl.prune(bsl.research(ur'^SymantecProtectionSuiteEnterpriseEdition', where='target'))
bsl.prune(bsl.research(ur'^(Note:|Notice|If|Uncomment|Log level|Do |We |Switch|However|You|Local database|How to|No more|The|That|Please|Apply|Prevent|Performance|Select|Obtain|Maximum|1\)|\d\) Se|Static|all Service|Sizing|Set |Current|registered|A |files|con 2|Allow |on |space|Insufficient|Configur|summarize)', where='target'))
bsl.prune(bsl.research(ur'^(msiexec|Yes|<!|!--|<service|<date|filter|rule|\[Y|PING|route|Cache Usage)', where='target'))
bsl.prune(bsl.research(ur'^(4 GB on|4 GB for|4 GB RAM|4 packet|512 MB RAM|60 GB|Internet Information Services server|1 GB RAM minimum|1 GB RAM \(2-|VGA \(640x480\) or|XGA \(1,024x768\) or|64-bit|32-bit|64 bytes|300 MB|256 MB|Citrix Metaframe|Terminal Server client|Windows client)', where='target'))
bsl.prune(bsl.research(ur'^(ENABLED|DISABLED)', where='target'))
bsl.prune(bsl.research(ur'(ENABLED|DISABLED)$', where='target'))
bsl.prune(bsl.research(ur'on-demand authentication radius add name alias_name server', where='target'))
bsl.prune(bsl.research(ur'^for one of the following', where='source'))
bsl.prune(bsl.research(ur'64 versions', where='target'))
bsl.prune(bsl.research(ur'IP ip address', where='target'))
bsl.prune(bsl.research(ur'has detected', where='target'))

bsl.rereplace(u'[\u2028\u25B2\uFF4A]', u'')
bsl.rereplace(u'[\u00A0\u200B\u3000]', u' ')
bsl.replace(u'１', u'1')
bsl.replace(u'ｔｌｓ', u'tls')
bsl.replace(u'Ｇ', u'G')
bsl.replace(u'ＩＰ', u'IP')

bsl.replace(u'アプリカーション', u'アプリケーション', where='target')
bsl.replace(u'オペテーティング', u'オペレーティング', where='target')
bsl.replace(u'クライアンソフトウェア', u'クライアントソフトウェア', where='target')
bsl.replace(u'クライアントールール', u'クライアントルール', where='target')
bsl.replace(u'ファイフィンガープリント', u'ファイルフィンガープリント', where='target')
bsl.replace(u'リジストリ', u'レジストリ', where='target')
bsl.replace(u'アカウンが', u'アカウントが', where='target')
bsl.replace(u'サウネット', u'サブネット', where='target')
bsl.replace(u'良く寄せられる', u'よく寄せられる', where='target')
bsl.replace(u'送信さする', u'送信する', where='target')
bsl.replace(u'（エンタープライズ版のそ）', u'（エンタープライズ版のみ）', where='target')
bsl.replace(u'無効にてから', u'無効にしてから', where='target')
bsl.replace(u'はすします', u'はずします', where='target')
bsl.replace(u'ステータを', u'ステータスを', where='target')
bsl.replace(u'アンストール', u'アンインストール', where='target')
bsl.replace(u'セキュリテについて', u'セキュリティについて', where='target')
bsl.replace(u'セション', u'セッション', where='target')
bsl.replace(u'デフォルのトポート番号', u'デフォルトのポート番号', where='target')
bsl.replace(u'にリクスが', u'にリスクが', where='target')
bsl.replace(u'管理者のベント', u'管理者のイベント', where='target')
bsl.replace(u'EPA の 種類', u'EAP の 種類', where='target')
bsl.prune(bsl.search(u'ネットワークの検出と共の', where='target'))
bsl.prune(bsl.search(u'きれい', where='target'))
bsl.prune(bsl.search(u'ローカルクライアントコンピュータ一方別のケースで', where='target'))

bsl.replace(u'クォードコア', u'クアッドコア', where='target')

bsl.replace(u'インタフェース', u'インターフェース', where='target')
bsl.replace(u'エクスプローラー', u'エクスプローラ', where='target')
bsl.replace(u'エディター', u'エディタ', where='target')
bsl.replace(u'コンセントレイタ', u'コンセントレータ', where='target')
bsl.replace(u'コンピューター', u'コンピュータ', where='target')
bsl.rereplace(ur'サーバ(?!ー)', u'サーバー', where='target')
bsl.rereplace(ur'スライダ(?!ー)', u'スライダー', where='target')
bsl.replace(u'セキュリティー', u'セキュリティ', where='target')
bsl.rereplace(ur'ダイヤラ(?!ー)', u'ダイヤラー', where='target')
bsl.replace(u'データーベース', u'データベース', where='target')
bsl.replace(u'マネージャー', u'マネージャ', where='target')
bsl.rereplace(ur'メッセンジャ(?!ー)', u'メッセンジャー', where='target')
bsl.replace(u'ベンダー', u'ベンダ', where='target')
bsl.replace(u'ディザスター', u'ディザスタ', where='target')
bsl.rereplace(ur'クエリ(?!ー)', u'クエリー', where='target')
bsl.replace(u'ウイザード', u'ウィザード', where='target')
bsl.replace(u'ウィルス', u'ウイルス', where='target')
bsl.replace(u'ウインドウ', u'ウィンドウ', where='target')

bsl.replace(u'あてはまる', u'当てはまる', where='target')
bsl.replace(u'ユーザー名有り', u'ユーザー名あり', where='target')
bsl.replace(u'隠蔽', u'隠ぺい', where='target')
bsl.replace(u'行なうことができます', u'行うことができます', where='target')
bsl.replace(u'を行なわないと', u'を行わないと', where='target')
bsl.replace(u'およぼさずに', u'及ぼさずに', where='target')
bsl.replace(u'に関わらず', u'にかかわらず', where='target')
bsl.replace(u'ヶ月', u'カ月', where='target')
bsl.replace(u'稼働', u'稼動', where='target')
bsl.replace(u'箇所', u'個所', where='target')
bsl.replace(u'代りに', u'代わりに', where='target')
bsl.replace(u'切り換え', u'切り替え', where='target')
bsl.replace(u'越えて', u'超えて', where='target')
bsl.replace(u'様々な', u'さまざまな', where='target')
bsl.replace(u'従って 1 つの', u'したがって 1 つの', where='target')
bsl.replace(u'お奨めします', u'お勧めします', where='target')
bsl.replace(u'既に', u'すでに', where='target')
bsl.replace(u'素早く', u'すばやく', where='target')
bsl.replace(u'全ての', u'すべての', where='target')
bsl.replace(u'尋ねる', u'たずねる', where='target')
bsl.replace(u'直ちに', u'ただちに', where='target')
bsl.replace(u'次の通り', u'次のとおり', where='target')
bsl.replace(u'と共に', u'とともに', where='target')
bsl.replace(u'接続し直します', u'接続しなおします', where='target')
bsl.replace(u'はじめて', u'初めて', where='target')
bsl.replace(u'外すには', u'はずすには', where='target')
bsl.replace(u'ひそかに', u'密かに', where='target')
bsl.replace(u'ほうが', u'方が', where='target')
bsl.replace(u'みなされ', u'見なされ', where='target')
bsl.replace(u'とみなし', u'と見なし', where='target')
bsl.replace(u'とみなす', u'と見なす', where='target')
bsl.replace(u'もっとも', u'最も', where='target')
bsl.replace(u'もともと', u'元々', where='target')
bsl.replace(u'わからない', u'分からない', where='target')

bsl.replace(u'アドレス宛ての', u'アドレス宛の', where='target')
bsl.replace(u'切替える', u'切り替える', where='target')
bsl.replace(u'書き込と', u'書き込みと', where='target')
bsl.rereplace(ur'支払(?!い)', u'支払い', where='target')
bsl.rereplace(ur'更新済(?!み)', u'更新済み', where='target')
bsl.rereplace(ur'手続(?!き)', u'手続き', where='target')
bsl.replace(u'問合せ', u'問い合わせ', where='target')
bsl.replace(u'取付け', u'取り付け', where='target')

bsl.trim()
bsl.prune(bsl.empty())
bsl.duprune(bsl.duplicate(where='both'))
print len(bsl)


import nltk
import MeCab

mtagger = MeCab.Tagger('-Owakati -u %s' % myenv.projfile('mydic.dic'))

def sourcetokenize(text):
    return u' '.join(nltk.word_tokenize(text))

def targettokenize(text):
    return mtagger.parse(text.encode('utf-8')).decode('utf-8').strip()

bsl.tokenize(sourcetokenize, targettokenize)

# bsl.write_text(myenv.tmxV+'.en', myenv.tmxV+'.ja', sourceencoding='utf-8', targetencoding='utf-8')


def contains(small, big):
    for i in xrange(len(big)-len(small)+1):
        for j in xrange(len(small)):
            if big[i+j] != small[j]:
                break
        else:
            return i, i+len(small)
    return False

# trm = BilingualSegmentList().read(format='tabbed', name=myenv.tmxV+'.anymalign_term.txt', encoding='utf-8')
# passed = []
# failed = []
# for i, (s, t) in enumerate(bsl):
#     s, t = s.split(), t.split()
#     result = 0
#     words = []
#     for ts, tt in trm:
#         if contains(ts.split(), s):
#             words.append((ts, tt))
#             if not contains(tt.split(), t):
#                 result = -1
#                 break
#             result = 1
#     if result == 1:
#         passed.append((u' '.join(s), u' '.join(t), words))
#     elif result == -1:
#         failed.append((u' '.join(s), u' '.join(t), words))
#     print '\r{}/{}'.format(i, len(bsl)),
# print '===== PASSED ====='
# up.pprint(passed)
# print '===== FAILED ====='
# up.pprint(failed)




bsl.moses_escape()
bsl.moses_truecase(where='source', source_model_name=myenv.tmxV+'.truecasemodel.en')

import random
random.shuffle(bsl)

trnmax = int(1.0 * len(bsl) * 0.9)
tunmax = int(1.0 * len(bsl) * 0.95)
training = bsl[:trnmax]
training.cutoff()
training.write(format='text', name=(myenv.tmxV+'.trn.en', myenv.tmxV+'.trn.ja'), encoding='utf-8')
bsl[trnmax:tunmax].write(format='text', name=(myenv.tmxV+'.tun.en', myenv.tmxV+'.tun.ja'), encoding='utf-8')
bsl[tunmax:].write(format='text', name=(myenv.tmxV+'.eva.en', myenv.tmxV+'.eva.ja'), encoding='utf-8',)
