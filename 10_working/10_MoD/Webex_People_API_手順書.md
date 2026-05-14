# Webex People API 手順書
## ADユーザー情報をControl Hubに反映する

**目的**：Active Directory の変更を Webex Control Hub へ People API 経由で直接反映する  
**ツール**：Postman  
**参照ドキュメント**：https://developer.webex.com/admin/docs/api/v1/people

---

## 事前準備

### 1. 管理者アクセストークンの取得

1. https://developer.webex.com にログイン（Control Hub 管理者アカウント）
2. 右上のアカウントアイコン → **「Copy personal access token」**をクリック
3. トークン（有効期限12時間）をコピーして保管

> ⚠️ 本番運用ではOAuth 2.0 Service Account（長期トークン）の利用を推奨  
> ラボ検証ではPersonal Access Tokenで問題なし

### 2. Postman の準備

1. Postmanを起動
2. 同梱の `Webex_People_API.postman_collection.json` をインポート  
   （File → Import → ファイルを選択）
3. コレクションの「Variables」タブを開き、以下を設定：

| 変数名 | 設定値 |
|--------|--------|
| `base_url` | `https://webexapis.com/v1` |
| `access_token` | 手順1で取得したトークン |
| `target_email` | テスト対象ユーザーのメールアドレス |
| `person_id` | ※後の手順で取得してから入力 |
| `license_id` | ※後の手順で取得してから入力 |

---

## 作業フロー概要

```
[Step 1] ライセンスID確認
      ↓
[Step 2] ユーザー検索（AD対象者が既にControl Hubに存在するか確認）
      ↓
  ┌─────────────────────────────┐
  │ 存在しない            存在する │
  ↓                        ↓
[Step 3a]              [Step 3b]
新規作成（POST）       情報更新（PUT）
  └──────────────┬──────────────┘
                 ↓
        [Step 4] 反映確認（GET）
```

---

## Step 1：ライセンスID確認

**目的**：ユーザー作成時に指定するライセンスIDを確認する

| 項目 | 値 |
|------|-----|
| Method | GET |
| URL | `{{base_url}}/licenses` |
| Headers | `Authorization: Bearer {{access_token}}` |

**実行後の確認**：  
レスポンスの `items[].id` を控える。  
Webex Calling に対応するライセンスの `name` を確認し、その `id` を Postman の変数 `license_id` に設定する。

```json
{
  "items": [
    {
      "id": "XXXXXXXXXXXXXXXXXXXXX",
      "name": "Webex Calling - Professional",
      "totalUnits": 100,
      "consumedUnits": 42
    }
  ]
}
```

---

## Step 2：ユーザー検索（存在確認）

**目的**：ADから取得したメールアドレスが Control Hub に存在するか確認する

| 項目 | 値 |
|------|-----|
| Method | GET |
| URL | `{{base_url}}/people?email={{target_email}}` |
| Headers | `Authorization: Bearer {{access_token}}` |

**判定**：
- `items` が空配列 → Step 3a（新規作成）へ
- `items[0]` が存在する → `items[0].id` を `person_id` 変数に設定して Step 3b（更新）へ

---

## Step 3a：新規ユーザー作成（ADにいてControl Hubに未登録の場合）

| 項目 | 値 |
|------|-----|
| Method | POST |
| URL | `{{base_url}}/people` |
| Headers | `Authorization: Bearer {{access_token}}` |
| Headers | `Content-Type: application/json` |

**Request Body（JSON）**：

```json
{
  "emails": ["user01@example.com"],
  "firstName": "Taro",
  "lastName": "Yamada",
  "displayName": "Taro Yamada",
  "department": "IT部",
  "title": "エンジニア",
  "phoneNumbers": [
    {
      "type": "work",
      "value": "+81312345678"
    }
  ],
  "licenses": ["{{license_id}}"]
}
```

**AD属性とBodyフィールドの対応表**：

| ADの属性名 | People API のフィールド | 必須 |
|-----------|------------------------|------|
| `mail` | `emails[0]` | ✅ |
| `givenName` | `firstName` | - |
| `sn` | `lastName` | - |
| `displayName` | `displayName` | - |
| `department` | `department` | - |
| `title` | `title` | - |
| `telephoneNumber` | `phoneNumbers[0].value` | - |
| `mobile` | `phoneNumbers[1].value` | - |
| ライセンスID（固定） | `licenses[0]` | ✅ |

**成功時レスポンス（200 OK）**：  
`id` フィールドを `person_id` 変数に保存する。

---

## Step 3b：既存ユーザー情報更新（ADの変更をControl Hubに反映）

| 項目 | 値 |
|------|-----|
| Method | PUT |
| URL | `{{base_url}}/people/{{person_id}}` |
| Headers | `Authorization: Bearer {{access_token}}` |
| Headers | `Content-Type: application/json` |

**Request Body（JSON）**：

```json
{
  "emails": ["user01@example.com"],
  "firstName": "Taro",
  "lastName": "Yamada",
  "displayName": "Taro Yamada",
  "department": "ネットワーク部",
  "title": "シニアエンジニア",
  "phoneNumbers": [
    {
      "type": "work",
      "value": "+81398765432"
    }
  ],
  "licenses": ["{{license_id}}"]
}
```

> ⚠️ PUT は全フィールドの送信が必要（PATCHではないため、省略するとクリアされる場合あり）

---

## Step 4：反映確認

| 項目 | 値 |
|------|-----|
| Method | GET |
| URL | `{{base_url}}/people/{{person_id}}` |
| Headers | `Authorization: Bearer {{access_token}}` |

**確認ポイント**：  
- `displayName`、`department`、`title`、`phoneNumbers` が更新値になっていること
- `status` が `active` であること
- Control Hub の画面（admin.webex.com）でも同一内容が表示されること

---

## Step 5（任意）：ユーザー削除

AD側でアカウントが無効化・削除された場合の対応

| 項目 | 値 |
|------|-----|
| Method | DELETE |
| URL | `{{base_url}}/people/{{person_id}}` |
| Headers | `Authorization: Bearer {{access_token}}` |

**成功時レスポンス**：204 No Content

---

## API 一覧まとめ

| No | 操作 | Method | エンドポイント | 用途 |
|----|------|--------|--------------|------|
| 1 | ライセンス取得 | GET | `/licenses` | ライセンスID確認 |
| 2 | ユーザー検索 | GET | `/people?email={email}` | ADユーザーの存在確認 |
| 3 | ユーザー詳細取得 | GET | `/people/{personId}` | 個人情報の確認 |
| 4 | ユーザー作成 | POST | `/people` | 新規ユーザーをControl Hubに追加 |
| 5 | ユーザー更新 | PUT | `/people/{personId}` | AD変更のControl Hubへの反映 |
| 6 | ユーザー削除 | DELETE | `/people/{personId}` | ADから削除されたユーザーの削除 |

---

## エラー対応

| HTTPステータス | 意味 | 対処 |
|--------------|------|------|
| 400 Bad Request | リクエスト形式エラー | Bodyの必須フィールド確認 |
| 401 Unauthorized | トークンが無効 | アクセストークンを再取得 |
| 403 Forbidden | 権限不足 | 管理者アカウントか確認 |
| 404 Not Found | personIdが存在しない | Step 2でIDを再取得 |
| 409 Conflict | メールアドレスが重複 | Step 2で検索してIDを取得してからPUTへ |

---

## 注意事項

1. **Directory Connector 由来ユーザーへの上書き**  
   Directory Connector で同期済みのユーザーに対しても People API での更新は可能。  
   ただし、次回 Directory Connector が同期した際に上書きされる可能性がある。  
   → ADとの二重管理にならないよう、運用フローを設計すること。

2. **メールドメインの制限**  
   Control Hub に登録されたドメイン配下のメールアドレスのみ作成可能。

3. **トークン有効期限**  
   Personal Access Token は12時間で失効。  
   継続運用ではサービスアカウント（OAuth 2.0）を使用すること。
