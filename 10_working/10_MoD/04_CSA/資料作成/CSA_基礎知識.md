# CSA_基礎知識

## 1. Cisco Secure Access (CSA) とは
Cisco Secure Access は、Cisco の SSE (Security Service Edge) 製品です。ゼロトラストの考え方を前提に、ユーザーがインターネット、SaaS、プライベートアプリへアクセスする際のセキュリティをクラウド提供でまとめて実装します。

公開資料上は、主に次の機能群を 1 つの管理基盤・単一クライアントで扱えることが特徴です。

- ZTNA
- VPNaaS
- SWG
- CASB
- FWaaS
- DLP
- DNS Security
- RBI
- DEM
- AI Access

厳密に「必ず 6 種類」と固定で定義されているわけではありません。ただし、実装検討の観点では、まず 6 つに整理して考えると分かりやすいです。

## 2. CSA を実装するうえで押さえたい 6 つの機能
実務上は次の 6 分類で考えると整理しやすいです。

### 2.1 Private Access
対象: 社内アプリ、IaaS 上のプライベートアプリ、管理系アクセス

含まれる代表機能:
- ZTNA
- VPNaaS

役割:
- 社内向けアプリを公開せずに安全に使わせる
- ユーザー/端末/姿勢情報に応じて最小権限で通す
- ZTNA で扱いづらいレガシー通信は VPNaaS で補完する

### 2.2 Internet / SaaS Access
対象: Web アクセス、SaaS 利用、一般インターネット通信

含まれる代表機能:
- SWG
- CASB

役割:
- URL やカテゴリ単位でアクセス制御する
- SaaS や Shadow IT の可視化を行う
- SaaS 上での危険操作や未承認利用を抑制する

### 2.3 Network Security
対象: Web 以外も含むポート/プロトコル単位の制御

含まれる代表機能:
- FWaaS
- IPS

役割:
- L3/L4/L7 の通信制御を行う
- Internet 向け、Private 向けの両方に対してルール適用できる
- Web プロキシでは扱いにくい通信もカバーしやすい

### 2.4 Data Protection
対象: 機密データの持ち出し、生成 AI への入力、SaaS へのアップロード

含まれる代表機能:
- DLP
- AI Access

役割:
- 個人情報、認証情報、ソースコードなどの流出を検知/抑止する
- AI ツールへの入力/出力も含めてガードレールを作る

### 2.5 Threat Protection
対象: 悪性ドメイン、危険サイト、不審ファイル

含まれる代表機能:
- DNS Security
- RBI
- Malware Analytics

役割:
- DNS レイヤで危険ドメインを早期遮断する
- 高リスクサイトは分離ブラウザで閲覧させる
- ダウンロードファイルの解析を行う

### 2.6 Visibility / Operations
対象: 運用監視、性能可視化、トラブルシュート

含まれる代表機能:
- DEM
- 統合ポリシー管理
- AI Assistant

役割:
- ユーザー体感、アプリ応答、ネットワーク品質を可視化する
- ポリシーを一元管理する
- 障害時に「回線か、SSE か、アプリか」を切り分けやすくする

## 3. 音声に関わる部分は何か
音声/通話品質に直接関わりやすいのは次の機能です。

### 3.1 最も重要
- FWaaS
- ZTNA / VPNaaS
- DEM

理由:
- 音声は遅延、ジッタ、パケットロスに敏感で、経路設計の影響を強く受けるため
- トンネル収容やクラウドヘアピンが増えると品質悪化リスクがあるため
- 品質問題を可視化するには DEM が重要なため

### 3.2 間接的に重要
- DNS Security
- SWG

理由:
- 音声そのものではなく、名前解決や signaling の制御面で影響するため
- signaling が HTTPS ベースなら SWG/プロキシ経由の設計が候補になるため

### 3.3 基本的には主役ではない
- CASB
- DLP
- RBI

理由:
- これらは SaaS 統制やデータ保護には重要だが、リアルタイム音声メディアそのものの品質向上には直結しにくいため

## 4. Webex 利用時に CSA の各機能がどう役立つか

### 4.1 Webex signaling
Webex App のクラウド登録型クライアントは、公開情報上 HTTPS signaling を使う部分が多く、プロキシや URL ベース許可との相性があります。

CSA で関係しやすい機能:
- SWG
- FWaaS
- DNS Security
- DEM

想定役割:
- Webex の必要ドメイン/URL を許可する
- 危険な宛先と Webex 正常通信を分離する
- signaling の到達性や失敗を可視化する

### 4.2 Webex media
音声/映像メディアはリアルタイム性が高く、一般に signaling よりも経路品質の影響を受けやすいです。

CSA で関係しやすい機能:
- FWaaS
- VPNaaS/ZTNA
- DEM

想定役割:
- 必要な UDP/TCP ポートの許可
- セキュリティポリシー適用
- 遅延/ジッタ/ロスの可視化

注意点:
- 音声メディアをクラウドセキュリティ経由で全面的にヘアピンさせると、品質面で不利になることがある
- セキュリティ優先で全通過にしたい場合も、事前の PoC が必須

### 4.3 Webex 向けに有用な CSA 機能まとめ
- SWG: signaling のドメイン/URL 制御
- FWaaS: signaling/media を含む広い通信制御
- DNS Security: 悪性宛先遮断
- DEM: Webex 品質監視
- ZTNA/VPNaaS: Webex 連携の社内周辺系アプリがある場合に有効
- CASB/DLP: Webex 上でのファイル共有やデータ持ち出し統制には有効

補足:
Cisco Secure Access の公開資料では、Cloud malware detection が Webex を対象 SaaS の一つとして挙げています。また DEM では Webex を含むコラボレーションアプリの性能可視化に言及があります。

## 5. CSA の従量課金について
公開 FAQ / Data Sheet を見る限り、Cisco Secure Access は基本的にトラフィック従量課金ではなく、ユーザー単位のサブスクリプションです。

公開情報で確認できる整理:
- Pricing は user-based
- SIA と SPA は別ユーザー数で購入可能
- Essentials / Advantage のパッケージ差分がある
- 一部は add-on がある

したがって、少なくとも公開資料ベースでは「イン方向/アウト方向の通信量で課金される」という説明は確認できませんでした。

実務上の読み替え:
- CSA 自体のライセンスは、通信量課金より seat 課金として考える
- ただし、回線費用、クラウド接続費、周辺製品ライセンスは別途考慮が必要
- 詳細見積は Cisco 見積資料かパートナー確認が必要

## 6. Webex で CSA を経由させている事例があるか
2026-05 時点で確認した公開ページの範囲では、「Webex の signaling/media を全面的に Cisco Secure Access に通している」と明示した事例は見つかっていません。

ただし、公開情報から言えることはあります。

確認できたこと:
- Cisco Secure Access は Web/SaaS/Private Access を広く保護対象にしている
- DEM は Webex を含むコラボレーションアプリの性能監視対象として扱っている
- Cloud malware detection の対象 SaaS に Webex が含まれている

未確認のこと:
- Webex Calling の signaling と media を全量 CSA 経由にした事例
- Webex Meetings/Calling を全面プロキシ or 全面 FWaaS 経由にしたリファレンス

結論:
- 部分的に CSA と Webex を組み合わせる設計は十分あり得る
- ただし「全ての Webex 通信を必ず CSA に通す」が公開ベストプラクティスとして示されているわけではない

## 7. SIPS / SRTP を CSA に通した際の負荷・費用

### 7.1 負荷面
SIPS / SRTP はリアルタイム通信なので、次の負荷が問題になります。

- 追加ホップによる遅延増加
- SSE POP 経由によるジッタ増加
- UDP の取り回し次第で品質変動
- 復号/検査の有無による処理負荷
- トンネル集約時の帯域圧迫

特に SRTP メディアは、セキュリティ装置を経由させるメリットより、品質劣化リスクのほうが先に問題になりやすいです。

### 7.2 費用面
公開資料ベースでは CSA は seat 課金なので、SIPS/SRTP を通したから直ちに従量課金で高くなる、とは読み取りにくいです。

ただし、実務では次をコストとして見ます。
- ユーザー数増加に伴う CSA ライセンス増
- Premium/Advantage/add-on の必要性
- 監視用途で ThousandEyes/DEM 関連ライセンスを足す可能性
- 帯域増や回線更改
- 音声品質担保のための PoC / 設計 / 運用コスト

## 8. signaling / media を CSA 経由にするべきか

### 8.1 signaling
signaling は HTTPS ベースであることが多く、URL/ドメイン許可やプロキシ制御との相性が比較的良いです。

そのため、signaling は次の設計が候補になります。
- SWG/Proxy 経由
- FWaaS 経由
- DNS Security + Firewall 制御

ただし Webex は signaling の IP アドレス固定運用を推奨しておらず、URL/ドメインベースの許可が重要です。

### 8.2 media
media は原則として品質優先で考えるべきです。

一般論としては次が無難です。
- media はできるだけ直接ブレイクアウト
- 必要最小限の FW 制御で通す
- 品質監視は DEM / ThousandEyes で補完
- どうしても通すならローカル拠点側での制御や最短経路を優先

### 8.3 ベストプラクティスの考え方
私見ではなく、公開資料と一般設計原則を踏まえると次の整理が妥当です。

- signaling: CSA を通す選択肢は十分ある
- media: 全量をクラウド SSE にヘアピンさせるのは慎重に判断すべき
- best practice は「全通し」より「通信種別ごとの最適経路分離」

## 9. 全て CSA を通す事例があるのか
技術的には、VPNaaS や FWaaS を用いてかなり広い範囲の通信を CSA に載せる構成は可能です。

ただし、次の理由から「全て通す」が常に最適とは限りません。
- リアルタイムメディアは遅延に弱い
- 音声品質よりセキュリティ検査を優先しすぎると UX が悪化する
- オフィス内や SD-WAN 拠点ではローカルブレイクアウトの方が合理的な場合がある
- Cisco も Hybrid Private Access の文脈で、クラウドだけでなくローカル enforcement の選択肢を示している

したがって、設計判断としては次の順が現実的です。
- まず signaling と media を分けて考える
- media は直通または最短経路を優先する
- 例外的に全通しが必要なら PoC で MOS、遅延、ジッタ、ロスを確認する

## 10. CSA 実装時の考え方まとめ

### 10.1 最低限決めるべきこと
- 何を Internet/SaaS として扱うか
- 何を Private Access として扱うか
- signaling と media を分離するか
- どこで TLS 復号/検査するか
- 音声/映像系はどこまで CSA に載せるか
- 監視を DEM まで入れるか

### 10.2 Webex を踏まえた現実的な初期方針
- Webex signaling は CSA 側で制御候補
- Webex media は原則として品質優先
- Webex 向けには URL/ドメイン許可とメディア経路の整理を先に行う
- 全通しを前提にせず、PoC で判断する

### 10.3 音声系で特に重要な CSA 機能
- FWaaS
- VPNaaS / ZTNA
- DEM
- DNS Security

## 11. 現時点の結論
- CSA は「6機能で考える」と整理しやすいが、製品としては 6 つに限定されない
- Webex で重要なのは、signaling と media を同じ扱いにしないこと
- CSA の公開価格情報は seat 課金ベースで、通信量従量課金とは読み取りにくい
- Webex を全面的に CSA 経由にした公開事例は、今回確認した範囲では見つかっていない
- signaling は CSA 経由の候補になりやすい
- media は直通または最短経路優先が基本で、全通しは PoC 前提

## 12. 参考にした公開情報
- Cisco Secure Access FAQ
  https://www.cisco.com/c/en/us/products/collateral/security/secure-access/secure-access-faq.html
- Cisco Secure Access Data Sheet
  https://www.cisco.com/c/en/us/products/collateral/security/secure-access/secure-access-ds.html
- Cisco Secure Access At a Glance
  https://www.cisco.com/c/en/us/products/collateral/security/secure-access/secure-access-cloud-security-sse-aag.html
- Network Requirements for Webex Services
  https://help.webex.com/en-us/article/WBX000028782/Network-Requirements-for-Webex-Services
