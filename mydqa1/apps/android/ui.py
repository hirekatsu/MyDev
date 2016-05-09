# -*- coding: utf-8 -*-

_lang = 'en'
_ui = {
    'en': {
        'Android': {},
        'WorkHub': {},
        'WorkWeb': {},
        'WorkMail': {},
        'WrapLib': {},
        'SWA': {},
        'MobileSecurity': {}
    },
    'ja': {
        'Android': {
            u'Copy': u'コピー',
            u'Cut': u'切り取り',
            u'Deny': u'Deny',
            u'Done': u'完了',
            u'OK': u'OK',
            u'Other Options': u'その他のオプション',
            u'Paste': u'貼り付け',
            u'Select all': u'すべて選択',
            u'Share': u'共有',
            u'Unfortunately': u'問題が発生したため'
        },
        'WorkHub': {
            u'Allow': u'許可',
            u'An error occurred during sign in': u'サインイン中にエラーが発生しました',
            u'Continue': u'続行',
            u'Deny': u'拒否',
            u'Device Ownership': u'デバイスの所有権',
            u'Home': u'ホーム',
            u'No': u'いいえ',
            u'Password': u'パスワード',
            u'requesting to join WorkSpace': u'ワークスペースへの結合を要求しています',
            u'Sign In': u'サインイン',
            u'User Name': u'ユーザー名'
        },
        'WorkWeb': {
            # Work Web UI has not been localized yet.
        },
        'WorkMail': {
            u'Awaiting Symantec Configuration': u'MDM 設定を待機中',
            u'Close': u'閉じる',
            u'Confirm': u'確認',
            u'Device Configuration Wizard': u'Device Configuration Wizard',
            u'Finished configuration': u'Finished configuration',
            u'I Accept': u'同意します',
            u'License Agreement': u'使用許諾契約書',
            u'Message': u'メッセージ',
            u'Next': u'次へ',
            u'Password': u'パスワード',
            u'Send Email': u'メールの送信',
            u'Subject': u'件名'

        },
        'WrapLib': {
            u'Authentication failed': u'認証に失敗しました',
            u'Exit': u'終了',
            u'Do you want this app to join a WorkSpace': u'このアプリをワークスペースに結合しますか',
            u'in the input box to continue': u'続行するには入力フィールドに',
            u'is not allowed to join the': u'ワークスペースへの結合を許可されていません',
            u'Join': u'結合',
            u'Login': u'ログイン',
            u'Network Issue': u'ネットワークの問題',
            u'NO': u'いいえ',
            u'OK': u'OK',
            u'Password:': u'パスワード:',
            u'Paste From...': u'貼り付け元...',
            u'Retry': u'再試行',
            u'Send data to': u'データを次に送信',
            u'sharing is not allowed': u'共有は許可されていません',
            u'System': u'システム',
            u'There is no proper app to open the data': u'データを開くのに適切なアプリがありません',
            u'Username:': u'ユーザー名:',
            u'Workspace': u'Workspace'
        },
        'SWA': {
            u'Refresh': u'更新'

        },
        'MobileSecurity': {
            u'Agree & Launch': u'同意して起動',
            u'Buy Now': u'今すぐ延長',
            u'Norton Mobile Security': u'ノートン モバイルセキュリティ'
        }
    }
}
Android = None
WorkHub = None
WorkWeb = None
WorkMail = None
WrapLib = None
SWA = None
MobileSecurity = None

class AppUi():
    def __init__(self, ui):
        self._ui = ui

    def get(self, sid):
        if isinstance(sid, str):
           sid = sid.decode('utf-8', 'ignore')
        ent = self._ui[sid] if sid in self._ui else sid
        return ent


def initialize(lang):
    global _lang, _ui, Android, WorkHub, WorkWeb, WorkMail, WrapLib, SWA, MobileSecurity
    if lang not in _ui:
        lang = 'en'
    _lang = lang
    Android = AppUi(_ui[_lang]['Android'])
    WorkHub = AppUi(_ui[_lang]['WorkHub'])
    WorkWeb = AppUi(_ui[_lang]['WorkWeb'])
    WorkMail = AppUi(_ui[_lang]['WorkMail'])
    WrapLib = AppUi(_ui[_lang]['WrapLib'])
    SWA = AppUi(_ui[_lang]['SWA'])
    MobileSecurity = AppUi(_ui[_lang]['MobileSecurity'])

