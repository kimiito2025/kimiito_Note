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
  - 開けない場合は、次のどれかで代替する
    - Import 画面の `Upload Files` ではなく、JSONファイルをPostman画面へドラッグ&ドロップする
    - Import 画面の `Raw text` タブに JSON の中身を貼り付けて `Import` する
    - エクスプローラーで JSON をデスクトップ等へコピーしてから選択する（OneDrive配下だと選択に失敗する場合がある）
3. コレクションの「Variables」タブを開き、以下を設定：

| 変数名 | 設定値 |
|--------|--------|
| `base_url` | `https://webexapis.com/v1` |
| `access_token` | 手順1で取得したトークン |
| `target_email` | テスト対象ユーザーのメールアドレス |
| `first_name` | 作成するユーザーの名 |
| `last_name` | 作成するユーザーの姓 |
| `display_name` | Control Hub表示名 |
| `department` | 部署名 |
| `title` | 役職 |
| `work_phone` | 勤務先電話番号 |
| `location_id` | Webex Calling 用の locationId |
| `extension` | Webex Calling 用の内線番号（任意） |
| `person_id` | ※後の手順で取得してから入力 |
| `license_id` | ※後の手順で取得してから入力 |

補足：
- Import 成功後は左ペインに `Webex People API - AD to Control Hub` が表示される
- 何も表示されない場合は Postman を再起動して再インポートする

---

## まずはこれだけ：3ステップで1ユーザー追加

この章だけ実施すれば、Postman から Control Hub へのユーザー追加を確認できる。

### Step A: 入力する値（Variables）

Postman コレクションの Variables に次を入れる。

| 変数名 | 例 |
|--------|----|
| `access_token` | 手順1で取得したトークン |
| `target_email` | `user01@example.com` |
| `first_name` | `Taro` |
| `last_name` | `Yamada` |
| `display_name` | `Taro Yamada` |
| `department` | `IT部` |
| `title` | `エンジニア` |
| `work_phone` | `+81312345678` |

### Step B: 押す順番

1. `Step 1: ライセンスID確認` を実行
2. レスポンスから使いたいライセンスの `id` を `license_id` に貼り付け
3. `Step 3a: ユーザー新規作成（標準ライセンス）` を実行
4. `Step 4: 反映確認（GET）` を実行

### Step C: 成功判定

- `Step 3a` が 200 なら作成成功
- `Step 4` で `status: active` なら反映完了

### つまずきやすいポイント

- 409 Conflict: そのメールアドレスは既に存在（別メールアドレスで再実行）
- 401 Unauthorized: トークン期限切れ（Personal Access Token を再取得）
- メールドメインは Control Hub 登録済みドメインのみ利用可能

### Webex Callingライセンスで作成する場合

Webex Calling ライセンスを使うときは、標準の Step 3a ではなく `Step 3a-C` を使う。

1. Step 1 で Webex Calling ライセンスの `id` を `license_id` に設定
2. Step 1.5 でロケーション一覧を取得し、対象拠点の `id` を `location_id` に設定
3. Variables に `work_phone`（または `extension`）を設定
4. `Step 3a-C: ユーザー新規作成（Webex Callingライセンス）` を実行
5. `Step 4: 反映確認（GET）` を実行

ロケーションID取得の詳細：
- Method: GET
- URL: `{{base_url}}/locations`
- Headers: `Authorization: Bearer {{access_token}}`
- レスポンス `items[].name` で拠点を選び、`items[].id` を `location_id` に設定

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

## Step 3a：新規ユーザー作成（標準ライセンス）

| 項目 | 値 |
|------|-----|
| Method | POST |
| URL | `{{base_url}}/people` |
| Headers | `Authorization: Bearer {{access_token}}` |
| Headers | `Content-Type: application/json` |

**Request Body（JSON）**：

```json
{
  "emails": ["{{target_email}}"],
  "firstName": "{{first_name}}",
  "lastName": "{{last_name}}",
  "displayName": "{{display_name}}",
  "department": "{{department}}",
  "title": "{{title}}",
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

## Step 3a-C：新規ユーザー作成（Webex Callingライセンス）

| 項目 | 値 |
|------|-----|
| Method | POST |
| URL | `{{base_url}}/people` |
| Headers | `Authorization: Bearer {{access_token}}` |
| Headers | `Content-Type: application/json` |

**Request Body（JSON）**：

```json
{
  "emails": ["{{target_email}}"],
  "firstName": "{{first_name}}",
  "lastName": "{{last_name}}",
  "displayName": "{{display_name}}",
  "department": "{{department}}",
  "title": "{{title}}",
  "locationId": "{{location_id}}",
  "extension": "{{extension}}",
  "phoneNumbers": [
    {
      "type": "work",
      "value": "{{work_phone}}"
    }
  ],
  "licenses": ["{{license_id}}"]
}
```

**ポイント**：
- Webex Calling ライセンスでは `locationId` が必要
- `phoneNumbers` または `extension` のいずれかが必要

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
  "emails": ["{{target_email}}"],
  "firstName": "{{first_name}}",
  "lastName": "{{last_name}}",
  "displayName": "{{display_name}}",
  "department": "{{department}}",
  "title": "{{title}}",
  "phoneNumbers": [
    {
      "type": "work",
      "value": "{{work_phone}}"
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
| 4 | ユーザー作成（標準） | POST | `/people` | 新規ユーザーをControl Hubに追加 |
| 5 | ユーザー作成（Webex Calling） | POST | `/people` | Webex Calling 情報付きで新規作成 |
| 6 | ユーザー更新 | PUT | `/people/{personId}` | AD変更のControl Hubへの反映 |
| 7 | ユーザー削除 | DELETE | `/people/{personId}` | ADから削除されたユーザーの削除 |

---

## エラー対応

| HTTPステータス | 意味 | 対処 |
|--------------|------|------|
| 400 Bad Request | リクエスト形式エラー | Bodyの必須フィールド確認 |
| 401 Unauthorized | トークンが無効 | アクセストークンを再取得 |
| 403 Forbidden | 権限不足 | 管理者アカウントか確認 |
| 404 Not Found | personIdが存在しない | Step 2でIDを再取得 |
| 409 Conflict | メールアドレスが重複 | Step 2で検索してIDを取得してからPUTへ |

### 追加メモ（400: Calling flag not set の場合）

`Calling flag not set` は、`license_id` に Webex Calling 系ライセンスを指定した際に発生しやすい。

まずは成功優先で、次のどちらかで対応する。

1. **最短回避（推奨）**  
  Step 1 で Webex Calling 以外のライセンスIDを `license_id` に設定して Step 3a を再実行する。

2. **Webex Callingユーザーとして作る場合**  
  Request Body に `locationId` を追加し、`phoneNumbers` または `extension` を必ず含める。

補足：Create a Person は 400 が返ってもユーザー自体は作成済みの場合があるため、失敗時は Step 2（`GET /people?email=...`）で存在確認してから再試行する。

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
