# API設計案: インポート後ユーザへの Calling 設定適用

## 前提
- ユーザ本体は AD/Entra 同期で Control Hub に作成済み。
- ライセンスはテンプレートで自動付与される想定（不足時は API で補正）。
- 目的は以下 3 点の自動化。
  - 内線番号（extension）
  - ハントグループ割り当て
  - ピックアップグループ割り当て

## 参照 API（公式カテゴリ）
- People API
  - https://developer.webex.com/admin/docs/api/v1/people/update-a-person
  - https://developer.webex.com/admin/docs/api/v1/people/list-people
- Calling Provisioning APIs ガイド
  - https://developer.webex.com/admin/docs/api/guides/webex-calling-provisioning-apis
  - ガイド内の Features: Hunt Group APIs
  - ガイド内の Features: Call Pickup APIs

注記:
- ハント/ピックアップの実エンドポイントは上記カテゴリ配下で確定する。
- 実装時はカテゴリページの Operation 一覧（List/Get/Create/Update）をそのまま採用する。

## 推奨フロー（バッチ/イベント共通）

### Step 0: 入力データ
- メールアドレス
- 付与する内線
- 所属 locationId
- ハントグループ名またはID
- ピックアップグループ名またはID

### Step 1: ユーザ同定
1. People 検索（メール）で personId を取得
2. 見つからない場合はリトライキューへ退避（同期遅延対策）

### Step 2: Calling 前提確認
1. ユーザの licenses に Calling があるか確認
2. locationId が有効か確認
3. 不足時はエラーではなく「前提未充足」として保留キューに移動

### Step 3: 内線設定（People API）
- PUT /people/{personId} で以下を反映
  - extension
  - locationId（必要条件を満たす場合）
  - phoneNumbers（必要なら）
- callingData=true を付け、応答に Calling 情報を含める
- PUT 失敗時でも一部属性が反映される可能性があるため、直後に GET で実状態を再確認

例（概念）:
{
  "emails": ["user@example.com"],
  "displayName": "Taro Yamada",
  "firstName": "Taro",
  "lastName": "Yamada",
  "locationId": "<locationId>",
  "extension": "1234",
  "licenses": ["<callingLicenseId>"]
}

### Step 4: ハントグループ割り当て
1. Hunt Group API で対象グループを取得（名称→ID解決）
2. メンバー/エージェント一覧を取得
3. personId を重複チェック後に追加
4. 更新 API 実行
5. 再取得して反映検証

### Step 5: ピックアップグループ割り当て
1. Call Pickup API で対象グループを取得（名称→ID解決）
2. メンバー一覧取得
3. personId を追加して更新
4. 再取得して反映検証

### Step 6: 監査ログ/再実行戦略
- trackingId を必ず保存
- 409 は冪等成功（既に所属）として扱う
- 429/5xx は指数バックオフで再試行
- 失敗は personId 単位で DLQ へ

## 実装パターン

### A. 夜間バッチ
- 同期完了後に CSV/DB を読み取り一括適用
- 長所: 運用が単純
- 短所: 反映遅延

### B. イベント駆動
- SCIM/同期イベントまたは定期差分検知で即時処理
- 長所: 反映が早い
- 短所: 再試行設計が必要

## テスト観点
- 正常系:
  - 新規同期ユーザに extension/ハント/ピックアップが反映される
- 異常系:
  - Calling ライセンス未付与
  - locationId 不正
  - 既にグループ所属済み
  - API レート制限

## 運用上の注意
- People API の PUT は全体更新性が強いため、変更前 GET→必要最小変更→PUT→再GETで検証する。
- ハント/ピックアップ更新は既存メンバー消し込み事故を避けるため、マージ更新を徹底する。
- 変更追跡のため、誰に何を適用したかを外部ログに残す。
