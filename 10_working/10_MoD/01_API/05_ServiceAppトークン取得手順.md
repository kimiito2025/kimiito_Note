# Service App トークン取得手順

## 目的
- 個人トークンではなく、Service App を使って機械ユーザとして長期運用できるトークン運用を行う。

## 全体像
1. Developer Portal で Service App を作成
2. Full Admin が Control Hub で承認
3. Access Token / Refresh Token を取得
4. Refresh Token で継続運用

参照:
- https://developer.webex.com/admin/docs/service-apps
- https://developer.webex.com/docs/integrations

## 前提条件
- Service App を作成する開発者アカウントがある
- 承認できる Full Admin がいる
- 必要スコープが明確化されている

## 手順A: ポータルで取得する方法（最短）

### A-1. Service App 作成
1. https://developer.webex.com にログイン
2. My Webex Apps を開く
3. Create a New App -> Create a Service App
4. アプリ名、説明、スコープを設定
5. 発行された Client ID と Client Secret を保存

注意:
- Client Secret は一度しか表示されないため安全に保管する
- スコープは必要最小限にする

### A-2. 管理者承認
1. Service App 詳細画面で Request Admin Authorization を実行
2. Full Admin が Control Hub で承認
   - admin.webex.com -> Management -> Apps -> Service Apps
   - 対象 Service App を Authorize -> Save

### A-3. Token Pair 取得
1. Developer Portal の Service App 詳細画面を開く
2. Org Authorizations で承認済み組織を選択
3. Client Secret を入力
4. Access Token / Refresh Token を取得

補足:
- トークン期限の目安は Access 約14日、Refresh 約90日
- 実際の値はレスポンスの expires_in / refresh_token_expires_in を正とする

## 手順B: API で取得する方法（自動化向け）

Service App 画面を使わず API で token pair を取得できる。

出典:
- https://developer.webex.com/admin/docs/service-apps
  - Token retrieval via API

### B-1. 必要なもの
- Service App の appId
- clientId
- clientSecret
- targetOrgId
- Bearer token
  - Personal Access Token または
  - spark:applications_token スコープを持つ別 Integration の token

### B-2. リクエスト
- Method: POST
- URL: https://webexapis.com/v1/applications/{appId}/token
- Header:
  - Authorization: Bearer <token>
  - Content-Type: application/json
- Body:
{
  "clientId": "<service_app_client_id>",
  "clientSecret": "<service_app_client_secret>",
  "targetOrgId": "<org_id>"
}

### B-3. レスポンス
- access_token
- refresh_token
- expires_in
- refresh_token_expires_in

## 運用（更新）

Refresh Token で Access Token を更新する。

出典:
- https://developer.webex.com/docs/integrations
  - Using the Refresh Token

- Method: POST
- URL: https://webexapis.com/v1/access_token
- Content-Type: application/x-www-form-urlencoded
- Body:
  - grant_type=refresh_token
  - client_id=<client_id>
  - client_secret=<client_secret>
  - refresh_token=<refresh_token>

推奨:
- 期限切れ直前ではなく余裕を持って更新
- 失敗時は trackingId を保存して再試行

## よくある詰まりどころ
- 403: 承認ロール不足（Full Admin 必須）
- unauthorized: clientSecret の貼り付けミス
- scope 過多: Service App の scope 文字列上限に抵触
- Compliance scope 使用時: Full Admin かつ Compliance Officer が必要

## 実務向けのすすめ方
1. まずは手順Aで1回トークン取得して動作確認
2. 次に手順Bで自動化
3. 最後に Refresh 運用を定期ジョブ化
