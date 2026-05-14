# CONTEXT

## ルール
- わからないことがあれば必ず質問する
- **CONTEXT.md と TODO.md を都度更新**してセッション引き継ぎを維持する
- 日本語で回答する
- セッション開始時に CONTEXT.md を読んで状況を把握する
- **事実と推論を明確に区別する。推論を述べる際は「これは私の推論ですが」と必ず明示する。根拠が曖昧な場合は断定しない。**
- **Cisco Professional Services であるため、公式サポートへの問い合わせは不可。全て自己解決が必須。**

## Directory Connector 操作API - 調査完了
**事実：**
- Hybrid Connectors APIには取得のみ（GET）で、操作系エンドポイント（POST/PUT/DELETE）がない
- Cisco公開APIレベルでは Directory Connector 同期トリガーAPI は存在しない

**Ciscoが提供する機能：**
- ✅ Directory Connector情報取得
- ❌ Directory Connector設定変更
- ❌ Directory Connector同期トリガー
- ✅ Users API/Devices APIによるユーザー・デバイス直接操作

**制約下での実装方針：**
1. AD側で変更検知 → Webex Users/Devices APIで直接更新（AD→Webexの単向同期）
2. SCIM 2.0プロトコル経由での自動同期検討
3. Directory Connector ローカルツール（CLI/PowerShell）のトリガー制御

