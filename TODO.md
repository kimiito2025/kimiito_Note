# TODO

## PJ_MoD
- [ ] MoDのヒアリング項目確認
- [ ] MoDコールルート考える
- [ ] SD-WANの環境確認
- [x] ADサーバの修正がCHのWebex Callingに自動反映できるか調査
  - [x] Directory Connector操作APIの確認 → **公開APIに同期トリガー機能なし**
  - [ ] SCIM 2.0 APIでのユーザープロビジョニング機能を確認
  - [ ] ローカルツール（CLI/PowerShell）でのトリガー可能性を検証
  - [ ] Users/Devices APIによる直接更新方式を検討
- [ ] Webex API/CSVによるユーザー・デバイス一括登録/更新方法を調査
- [ ] Webex Calling RBACベータの要件適合性（ロケーション単位管理）を検証
- [ ] 01_API成果物のAPI実機検証を実施
  - [ ] 03_Postman_Collection_Import後Calling適用.json の基本動作確認（0→2）
  - [ ] Step 2（People PUT）の更新項目欠落リスク確認（GET→PUT→GETで差分検証）
  - [ ] ハントグループAPIの実エンドポイント確定（list/get/update URL変数を固定化）
  - [ ] ピックアップグループAPIの実エンドポイント確定（list/get/update URL変数を固定化）
  - [ ] hunt/pickup 更新のBodyスキーマ確定（agents/membersの必須項目を検証）
- [ ] Service Appトークン運用の実機検証を実施
  - [ ] 05_ServiceAppトークン取得手順.md のGUI手順で token pair 取得
  - [ ] /applications/{appId}/token でAPI取得できるか検証
  - [ ] refresh_token で access_token 更新できるか検証
  - [ ] 期限切れ・403時の再試行/運用手順を確定

## その他
- [ ] onenoteの情報を基に検索できるようにする
- [ ] シスコ社員がCisco Communityにコメント投稿してよいか確認（https://community.cisco.com/t5/webex-administration/uccx-aef-script-upload-and-convert-on-webex-contact-center/m-p/4532392#M3676）

