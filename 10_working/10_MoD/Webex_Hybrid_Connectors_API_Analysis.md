# Webex Developer API - Hybrid Connectors API 詳細調査

**調査日**: 2026年5月13日  
**調査対象**: https://developer.webex.com/admin/docs/api/v1/hybrid-connectors

---

## 📋 調査概要

Cisco Webex の Hybrid Connectors APIドキュメントを詳細に調査し、Directory Connectorの操作可能性、特に同期トリガー機能の有無を確認しました。

**調査対象キーワード**:
- `sync`、`trigger`、`force`、`update`、`execute` を含むエンドポイント

---

## 🔍 調査結果：Hybrid Connectors API エンドポイント

### 1️⃣ 利用可能なエンドポイント一覧

Hybrid Connectors API には、**2つのエンドポイントのみ** が存在します：

#### エンドポイント① List Hybrid Connectors

```
GET /hybrid/connectors
```

**概要**
- 組織内のハイブリッドコネクターの一覧を取得
- 指定されていない場合、認証ユーザーの組織がデフォルト

**必要なスコープ**
```
spark-admin:hybrid_connectors_read
```

**リクエストパラメータ（クエリ）**
| パラメータ | 型 | 説明 | 例 |
|-----------|---|----|---|
| `orgId` | string | 対象組織。省略時は呼び出し元の組織 | `Y2lzY29zcGFyazovL3VzL09SR0FOSVpBVElPTi85NmFiYzJhYS0zZGNjLTExZTUtYTE1Mi1mZTM0ODE5Y2RjOWE` |

**レスポンス** (Status 200 OK)
```json
{
  "items": [
    {
      "id": "Y2lZY76123",
      "type": "calendar",
      "status": "operational",
      "version": "14.2.1",
      "hostname": "connector.company.com",
      "hybridClusterId": "cluster123",
      "orgId": "org456",
      "created": "2023-01-15T10:30:00Z",
      "alarms": []
    }
  ]
}
```

**エラーレスポンス**
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `429`: Too Many Requests

---

#### エンドポイント② Get Hybrid Connector Details

```
GET /hybrid/connectors/{connectorId}
```

**概要**
- 特定のハイブリッドコネクターの詳細情報を取得
- コネクターのステータス、バージョン、アラーム情報などを確認可能

**必要なスコープ**
```
spark-admin:hybrid_connectors_read
```

**リクエストパラメータ（パス）**
| パラメータ | 型 | 説明 | 例 |
|-----------|---|----|---|
| `connectorId` | string | 取得するコネクターのID（必須） | `Y2lZY76123` |

**レスポンス** (Status 200 OK)
```json
{
  "id": "Y2lZY76123",
  "type": "calendar",
  "status": "operational",
  "version": "14.2.1",
  "hostname": "connector.company.com",
  "hybridClusterId": "cluster123",
  "orgId": "org456",
  "created": "2023-01-15T10:30:00Z",
  "alarms": [
    {
      "id": "alarm123",
      "description": "Low disk space",
      "severity": "warning",
      "created": "2026-05-10T14:22:00Z"
    }
  ]
}
```

**コネクターステータス値**
- `operational`: 正常稼働中
- `impaired`: 機能低下状態
- `outage`: 停止状態
- `maintenanceMode`: メンテナンスモード

**コネクタータイプ値**
- `calendar`
- `call`
- `message`
- `expresswayManagement`
- `expresswayServiceability`

---

### 2️⃣ 操作系エンドポイント（POST、PUT、DELETE）の有無

**調査結果**: ❌ **存在しない**

- **POST** エンドポイント（作成）: なし
- **PUT** エンドポイント（更新）: なし
- **PATCH** エンドポイント（部分更新）: なし
- **DELETE** エンドポイント（削除）: なし

### 3️⃣ 同期関連エンドポイントの有無

**調査対象キーワード**

| キーワード | 検索結果 | 備考 |
|-----------|---------|------|
| `sync` | ❌ なし | 同期トリガーエンドポイントなし |
| `trigger` | ❌ なし | トリガー実行エンドポイントなし |
| `force` | ❌ なし | 強制実行エンドポイントなし |
| `update` | ❌ なし | 更新操作エンドポイントなし |
| `execute` | ❌ なし | 実行エンドポイントなし |

---

## 🚫 Directory Connector に関する重要な発見

### 同期操作の制限

**Hybrid Connectors API では以下の操作が不可能です**：

1. ❌ Directory Connector の同期を即座にトリガーする
2. ❌ 同期スケジュールを変更する
3. ❌ 同期の強制実行
4. ❌ コネクターの設定変更
5. ❌ コネクターの作成・削除

### 可能な操作

✅ Hybrid Connectors APIで可能なこと：

1. **コネクター一覧の取得** - 組織内の全コネクター情報を参照
2. **コネクター詳細の確認** - 特定コネクターのステータス、バージョン、アラーム確認
3. **ステータス監視** - コネクターの運用状態監視
4. **アラーム確認** - 未解決アラームの確認

---

## 📡 代替手段の検討

### 1. Directory Services API

**URL**: https://developer.webex.com/admin/docs/api/v1/directory-services

関連するサブAPI：
- API Domain Management
- Archived Users
- Identity Organization

**同期トリガー機能**: ❓ 要追加確認

### 2. SCIM 2.0 API

**用途**: ユーザープロビジョニング標準インターフェース

SCIM 2.0は DirectoryConnector と連携する可能性があります。
- ユーザー同期操作
- プロビジョニング自動化

**現状**: 未詳細確認

### 3. Webhooks

**用途**: リアルタイムイベント通知

Webex Webhooks では、以下のようなイベント取得が可能：
- ユーザー追加・更新・削除
- グループ管理
- ディレクトリ変更

**同期トリガー機能**: ❌ 通知のみで、トリガーなし

### 4. Control Hub UI

**現状**: GUIからの手動同期が可能な可能性あり
- "Sync Now" ボタンの有無確認必要
- UI でサポートされていても API で提供されていない機能の可能性

---

## 💡 推奨事項

### 優先度：高

1. **Cisco TAC への問い合わせ**
   - REST API 経由での同期トリガー機能の有無を確認
   - 非公開API の存在確認
   - バージョン別の機能サポート確認

2. **Directory Services API の詳細調査**
   - すべてのサブエンドポイントを確認
   - 同期関連操作の有無を確認

3. **Control Hub UI の確認**
   - GUI で同期トリガー機能があるか確認
   - あれば UI から使用可能な手動操作と考える

### 優先度：中

4. **SCIM 2.0 API の詳細検討**
   - ユーザープロビジョニング側からの同期メカニズム確認
   - Common Identity 経由での同期制御の可能性

5. **Directory Connector ローカルツール確認**
   - PowerShell インターフェース
   - CLI コマンド
   - Webhook リスナー

### 優先度：低

6. **他の Hybrid Connector 関連API の確認**
   - Hybrid Clusters API
   - Events API の Directory Connector イベント

---

## 📊 API 機能サマリー表

| 機能 | Hybrid Connectors API | Directory Services API | SCIM 2.0 | Webhooks |
|-----|:---:|:---:|:---:|:---:|
| コネクター参照 | ✅ | ✅ | ❓ | ❌ |
| コネクター作成 | ❌ | ❓ | ❓ | ❌ |
| コネクター更新 | ❌ | ❓ | ❓ | ❌ |
| コネクター削除 | ❌ | ❓ | ❓ | ❌ |
| **同期トリガー** | **❌** | **❓** | **❓** | **❌** |
| 同期スケジュール変更 | ❌ | ❓ | ❌ | ❌ |
| ユーザープロビジョニング | ❌ | ✅ | ✅ | ❌ |
| イベント通知 | ❌ | ❌ | ❓ | ✅ |

---

## 📚 参考リンク

- [Webex Hybrid Services](https://www.cisco.com/c/en/us/solutions/collaboration/webex-hybrid-services/index.html)
- [Webex 未解決アラーム情報](https://help.webex.com/nuej5gfb/)
- [Webex 開発者サポート](https://developer.webex.com/support)
- [Cisco Webex Developer Community](https://community.cisco.com/t5/webex-for-developers/bd-p/disc-webex-developers)

---

## 🎯 結論

**Directory Connector の同期をトリガーするパブリック REST API は、Webex Developer ドキュメントに記載されていません。**

次のステップ：
1. Cisco TAC に確認
2. Directory Services API 全体の詳細調査
3. Control Hub UI での手動操作可能性確認
4. ローカルツール（CLI/PowerShell）の検証
