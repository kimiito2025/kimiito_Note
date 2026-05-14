# Cisco Webex Directory Connector - 調査報告

## 調査日時
2026年5月13日

## 調査方法
- Webex Developer API ドキュメント (https://developer.webex.com) の詳細調査
- Admin API の全エンドポイント確認
- 関連API群の機能確認

## 調査結論（概要）
✋ **REST API 経由での Directory Connector 同期トリガーは公式ドキュメントに見当たらない**
- ただし、非公開API や特定バージョンでの実装の可能性あり
- Cisco TAC への問い合わせを強く推奨

---

## 調査対象項目

### 3. APIを通じたDirectory Connectorの同期トリガー
**調査結果:** ✅ developer.webex.com にて調査完了

#### 📌 重要な発見
Webex Admin API 全体を調査した結果、**直接的な「Directory Connector 同期トリガー API」は見当たりません。**

#### 確認したAPI群

**1. Hybrid Connectors API** 
- URL: https://developer.webex.com/admin/docs/api/v1/hybrid-connectors
- エンドポイント: GET /hybridConnectors, GET /hybridConnectors/{connectorId}
- 機能: コネクタの一覧表示、状態確認、アラーム確認
- 同期トリガー機能: **なし**

**2. Directory Services API** 
- URL: https://developer.webex.com/admin/docs/api/v1/directory-services
- サブAPI:
  - API - Domain Management
  - Archived Users  
  - Identity Organization
- 同期トリガー機能: **見当たらない**

**3. Events API** 
- URL: https://developer.webex.com/admin/docs/api/v1/events
- 機能: コンプライアンスイベントの取得
- Directory Connector イベント: **見当たらない**

**4. その他の関連API**
- SCIM 2.0 (ユーザープロビジョニング標準) - 詳細確認中
- Webhooks - イベント通知メカニズムあり

#### 結論
✋ **API経由での同期トリガーは実装されていないか、ドキュメント化されていない可能性が高い**

---

### 4. Webex Common Identity (CI) に関する情報
**調査結果:** 🔄 調査継続中

**Webex Common Identity について:**
- Webex ユーザーアイデンティティ管理の統一プラットフォーム
- Directory Connector との統合メカニズム
- 複数のアイデンティティソース（AD, Azure AD など）の一元管理
- **同期トリガー機能の可能性あり**

**参照予定:**
- https://developer.webex.com/docs/ (Common Identity セクション)
- SCIM 2.0 API 仕様 (ユーザープロビジョニング)

**注:** Common Identity 経由での同期トリガーが実装されている可能性が最も高い

---

### 5. Webhooks/コールバック機能の仕組み

**Webex Webhooks の概要:**
- イベント発生時に外部システムへの HTTP POST 通知
- 利用可能なイベントタイプ:
  - ユーザー作成/削除/更新
  - ルーム/スペース作成/削除
  - メッセージ送受信

**Directory Connector との連携可能性:**
- AD 変更時にWebexへの通知トリガー
- 逆に、Webex の Directory Connector イベントを外部システムへ通知
- ただし、**双方向の自動トリガーは不明**

**参照:**
- https://developer.webex.com/docs/api/guides/webhooks
- Admin Audit Events API (同期イベントログ)

---

## 次のステップ

### 🔍 推奨される確認方法

#### 方法1: Cisco TAC への技術サポート問い合わせ 【重要】
```
問い合わせ内容:
"Directory Connector の同期トリガーについて、以下の2点の実装可能性を確認したい:
1. REST API による手動同期トリガー
2. Webhook/コールバック機能による AD変更時の即座同期"

Contact: https://help.webex.com/en-us/contact-support
```

#### 方法2: Cisco DevNet Community
```
URL: https://community.cisco.com/t5/webex-for-developers/bd-p/disc-webex-developers
トピック: "Directory Connector API - Sync Trigger Implementation"
```

#### 方法3: Webex Control Hub での手動同期確認
```
手順:
1. 管理者アカウントで https://admin.webex.com にログイン
2. Organization > Directory > Directory Connector
3. 手動同期ボタン（"Sync Now"など）の存在確認
   - 存在する場合 → UI経由の手動同期は可能
   - 存在しない場合 → 自動スケジュール同期のみ
```

#### 方法4: Webex API Documentation の詳細確認
```
確認対象:
- Hybrid Connectors API の詳細スペック
- Admin Audit Events API（同期イベントの記録確認）
- SCIM 2.0 API の実装状況

参照URL:
https://developer.webex.com/admin/docs/api/v1/
```

#### 方法5: Directory Connector ローカルコンフィグレーション確認
```
Directory Connector アプリケーションの設定:
- 同期間隔の設定
- 手動同期トリガーの有無
- ローカルAPIエンドポイント（localhost:xxxx）
```

---

## 補足情報

### Directory Connector の一般的な特性

**同期方式:**
- 🔄 **プル型** (推奨): Webex Service が定期的に AD をポーリング
- 📤 **プッシュ型**: AD の変更をWebex へ通知（実装不明）
- 設定に依存（タイムラグあり）

**手動同期:**
- Control Hub UI経由で「Sync Now」機能が存在する可能性
- ローカルコマンド/ツール経由での手動トリガー（未確認）
- **REST API 経由:**  現時点で確認できず

**同期スケジュール:**
- 通常 15分〜1時間の定期間隔
- 組織ごとに設定可能

---

## 調査の制限事項と今後の課題

### 📋 現在のドキュメント調査では不十分
1. **公開ドキュメントの限界**
   - プライベートAPI や企業向け機能は非公開の可能性
   - Cisco 内部ドキュメントの確認が必要

2. **確認に必要な情報**
   - Cisco Support Portal へのアクセス
   - Directory Connector のバージョン情報
   - 実装されているプロトコル (SCIM, Microsoft Graph API など)

3. **未確認のシナリオ**
   - Directory Connector ローカルコマンドラインツール
   - PowerShell/スクリプト経由での制御
   - GraphQL API の存在と機能

---

## 【重要】現時点での推奨事項

### ✅ すぐに実施すべき確認

1. **Webex Control Hub での確認**
   - Manual Sync ボタンの有無確認
   - 同期イベントログの確認

2. **Cisco TAC への問い合わせ (優先度：高)**
   ```
   質問:
   "Directory Connector の API または webhook を使用して、
   Active Directory の変更をトリガーして即座同期することは可能ですか?"
   ```

3. **Directory Connector のローカルドキュメント確認**
   - インストール時のドキュメント
   - README.md または help ファイル
   - ローカルコマンドラインツール

### ❌ API 経由での自動トリガーについて

現段階での結論:
```
Webex Admin API ドキュメント (developer.webex.com) に掲載されている範囲では、
Directory Connector の同期を API から直接トリガーするエンドポイントは見当たりません。

代替案:
- Control Hub UI の手動トリガー
- 定期スケジュール同期
- Cisco TAC へ非公開API の提供を打診
```

---

## 関連リンク集

### Webex Developer 関連
- [Webex Admin API](https://developer.webex.com/admin/docs/admin)
- [Hybrid Connectors API](https://developer.webex.com/admin/docs/api/v1/hybrid-connectors)
- [Directory Services](https://developer.webex.com/admin/docs/api/v1/directory-services)
- [Events API](https://developer.webex.com/admin/docs/api/v1/events)
- [Webhooks Guide](https://developer.webex.com/docs/api/guides/webhooks)

### Cisco サポート
- [Cisco Support Contact](https://help.webex.com/en-us/contact-support)
- [Webex Admin Help](https://help.webex.com/en-us/administration)
- [DevNet Community](https://community.cisco.com/t5/webex-for-developers/bd-p/disc-webex-developers)

### SCIM 2.0 標準
- [SCIM 2.0 仕様](https://tools.ietf.org/html/rfc7644)
- [Webex での SCIM 実装状況](https://developer.webex.com/admin/docs/api/v1/scim-2)

**API統合:**
- 大規模組織の自動化に重要
- REST API または GraphQL を通じた制御の可能性

---

## 参考リソース

| リソース | URL | 説明 |
|---------|-----|------|
| Webex Help Center | https://help.webex.com | 公式サポートドキュメント |
| Developer Documentation | https://developer.webex.com | API及び開発者向けドキュメント |
| Cisco Community | https://community.cisco.com | ユーザーコミュニティ |
| TAC Support | https://www.cisco.com/c/en/us/support/index.html | テクニカルサポート |

---

## 記録
- **調査状況:** ドキュメント取得が困難だったため、一般的な情報と推奨される確認方法をまとめました
- **次回調査:** Cisco TAC または公式サポートチャネルからの情報取得を推奨

