# 証拠調査: ユーザ同期と Webex Calling 適用範囲

## 結論（先出し）
- AD/Entra 連携で Control Hub にユーザ情報が同期される仕様は、公式情報と整合する。
- ライセンスは Control Hub の自動ライセンス割り当てテンプレートで付与可能（Calling も対象）。
- 一方、内線番号・ハントグループ・ピックアップグループは「ユーザ同期属性」ではなく、Calling の個別設定/機能設定として別 API で管理するのが公式構成。
- つまり「ユーザ同期で自動反映」ではなく「同期後に Calling Provisioning API で適用」が正しい整理。

## 証拠一覧

### 1) ディレクトリ同期はディレクトリ起点で反映される
出典:
- https://help.webex.com/en-us/article/nikzbgy/Synchronize-Microsoft-Entra-ID-Users-into-Control-Hub

確認できた記述:
- Directory Connector 利用時は、Control Hub 側で再有効化/無効化/削除は行わず、Active Directory 側で実施して再同期する必要がある。
- 非アクティブユーザの扱いも「ディレクトリで無効化/削除された状態」が Webex 側に反映される説明になっている。

解釈:
- ユーザライフサイクル（作成/更新/無効化/削除）はディレクトリ同期で Control Hub に反映される。

### 2) ライセンステンプレートで自動付与できる（Calling 含む）
出典:
- https://help.webex.com/en-us/article/n3ijtao/Set-up-automatic-license-assignment-templates-in-Control-Hub

確認できた記述:
- 新規ユーザへ自動でライセンス付与できる。
- 組織単位/グループ単位どちらでも運用可能。
- AD グループ同期時、対象グループに設定したライセンスを新規ユーザへ付与可能。
- FAQ にて「Webex Calling ライセンスをライセンス割り当てで付与できるか」に Yes と明記。

解釈:
- セールス説明の「テンプレートでライセンス適用」は公式仕様と一致。

### 3) 同期属性（SCIM）には Calling 機能オブジェクトが含まれない
出典:
- https://developer.webex.com/admin/docs/scim-2-overview

確認できた記述:
- SCIM の管理対象は User/Group リソース。
- Supported attributes は userName, emails, name, department, title, phoneNumbers などユーザ属性中心。

解釈:
- ハントグループやピックアップグループのような Calling 機能オブジェクトは SCIM 同期の主対象ではない。
- よって「ユーザ同期だけで Calling 機能設定まで自動反映」は期待しにくい。

### 4) Calling 機能は Provisioning APIs の別カテゴリで管理
出典:
- https://developer.webex.com/admin/docs/api/guides/webex-calling-provisioning-apis

確認できた記述:
- Calling Features APIs として、機能別に API が分離されている。
- Features: Hunt Group APIs
- Features: Call Pickup APIs

解釈:
- ハント/ピックアップは、ユーザ同期や単純な People 同期とは別レイヤの API 管理対象。

### 5) 内線・ロケーションは Calling ライセンス条件付きで People API から設定
出典:
- https://developer.webex.com/admin/docs/api/v1/people/create-a-person
- https://developer.webex.com/admin/docs/api/v1/people/update-a-person

確認できた記述:
- phoneNumbers は Webex Calling 向けのみ設定可。
- extension は Webex Calling ライセンスがある人のみ設定可。
- locationId は Calling ライセンス付与時に扱う制約がある。
- Create 時に Calling ユーザを作るなら phoneNumbers または extension、locationId、licenses を同時指定する注意書きあり。

解釈:
- 内線設定は「同期属性の自動反映」よりも「Calling 条件を満たした API 設定」側の性質が強い。

## まとめ（証拠ベースの判断）
- 断定できること:
  - ユーザ同期はディレクトリ主導で反映される。
  - ライセンステンプレートで Calling を含む自動ライセンス付与が可能。
  - Calling 機能（Hunt/Call Pickup）は専用 Provisioning API カテゴリがある。
- 実務判断:
  - インポート後ユーザへの内線/ハント/ピックアップ適用は、同期機能に寄せるのではなく Provisioning API で後段実装する。
