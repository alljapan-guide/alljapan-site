# 公開から収益化までの手順書（上から順に実行）

作成日: 2026-10-18。画面の表記や条件は変わります。各ステップの公式ページで最新を確認してください。
このPCの環境からは公式ページを直接開けなかったため、手順は検索で取得した公式ページの記載に基づいています（出典を各所に付けました）。

## 全体の流れ

| 順 | 何をするか | 誰が | 目安 |
|---|---|---|---|
| 1 | リポジトリを自分専用にし、main に反映 | あなた | 30分 |
| 2 | ドメインを取得 | あなた | 15分 |
| 3 | GitHub Pages を設定（公開先） | あなた | 30分 |
| 4 | `config/site.json` を編集 | あなた（またはClaudeに依頼） | 10分 |
| 5 | Anthropic API キーを登録（記事の自動生成用） | あなた | 20分 |
| 6 | 初回実行と事実確認の結果チェック | あなた＋Claude | 30分 |
| 7 | Search Console に登録 | あなた | 20分 |
| 8 | アフィリエイト登録（順番が重要） | あなた | 数日〜数週間 |
| 9 | 提携リンクを貼る | あなた | 10分 |
| 10 | 毎週・毎月の運用 | 自動＋あなた | 週15分 |

重要: アフィリエイトの登録は、サイトを公開して記事が数本ある状態にしてからです（ステップ8）。登録時にサイトの審査があるためです。

---

## ステップ1: リポジトリを自分専用にする

今は `ec-pb-dashboard` リポジトリの `claude/japan-affiliate-site` ブランチにあります。売上ダッシュボードとは別物なので、専用リポジトリに分けることを推奨します。

1. GitHub で新しいリポジトリを作る（例: `japan-compass`）。公開（Public）か非公開かは、GitHub Pages のプラン条件に依存します。無料プランでは公開リポジトリが無難です。条件は [GitHub Docs: Pages](https://docs.github.com/en/pages) で確認してください。
2. `japan_affiliate/` フォルダ**ごと**（フォルダ名もそのまま）と `.github/workflows/japan-affiliate-publish.yml` を、新リポジトリにコピーします。ワークフローが `japan_affiliate/` フォルダを前提にしているため、構成を変えなければ編集は不要です。
3. 定期実行（毎日）は、GitHub の仕様上、デフォルトブランチ（通常は main）にあるワークフローだけが動きます。必ず main に反映してください。

## ステップ2: ドメインを取得

1. 候補: Cloudflare Registrar。ドメインを原価（上乗せなし）で売る仕組みです。公式: [Cloudflare Registrar](https://www.cloudflare.com/products/registrar/)、[FAQ](https://developers.cloudflare.com/registrar/faq/)。
2. Cloudflare のアカウントを作り（メール認証、支払い方法の登録が必要）、`.com` などを検索して購入します。
3. 価格は購入画面の合計が正です。年額は毎年変わるので、この文書には書きません。
4. ドメイン名は、サイト名（現在の仮名は Japan Compass）に合わせます。後から変更もできますが、検索評価がリセットされるので、最初に決めきってください。

## ステップ3: GitHub Pages を設定

公式: [Configuring a publishing source](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)、[Managing a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)

1. リポジトリの Settings → Pages → Build and deployment → Source を **GitHub Actions** にします。
2. 同じ画面の Custom domain に、取得したドメインを入力して保存します（GitHub の公式ドキュメントによると、Actions で公開する場合は CNAME ファイルは不要で、ドメインはこの設定画面で登録します）。
3. DNS（Cloudflare の DNS 設定）に次を追加します（公式ドキュメントの記載）。
   - `www` サブドメイン: CNAME レコードで `<ユーザー名>.github.io` を指す（リポジトリ名は付けない）。
   - ルートドメイン（`example.com`）: CNAME は使えないため、A、ALIAS、または ANAME レコードを使う。具体的な A レコードの値は、[GitHub Docs の最新ページ](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)の値を使ってください。
   - ワイルドカード（`*.example.com`）は使わない。公式が乗っ取りのリスクを警告しています。
4. 「Enforce HTTPS」にチェックを入れます（証明書の発行に少し時間がかかります）。
5. 任意ですが推奨: ドメイン所有の確認（TXT レコード）。公式: [Verifying your custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages)。他人があなたのドメインを使うことを防ぎます。

## ステップ4: `config/site.json` を編集

| 項目 | 何を入れるか |
|---|---|
| `base_url` | `https://あなたのドメイン`（末尾のスラッシュなし）。サイトマップとcanonical（正規URL）に使われます |
| `contact_email` | プライバシーページに載る連絡先メール。**未設定だと本番ビルドが止まります**（意図した安全装置） |
| `name` / `tagline` | サイト名と説明 |
| `author` | 発行者名（法人名か運営名）。実在しない人物名は使わないでください |

## ステップ5: 記事の自動生成を動かす準備

自動生成には Anthropic の API を使います。費用の目安: Anthropic の公式モデル表で、Claude Opus 5.5 は入力100万トークンあたり $4、出力 $20 です（2026-10 時点）。1記事で入力2万・出力2万トークンと仮定すると約 $0.5 です。仮定なので、実際は請求画面で確認してください。

1. [Anthropic Console](https://console.anthropic.com/) でアカウントを作り、支払い方法を登録し、**月の利用上限を必ず設定**します。
2. API キーを作成し、コピーします（画面を閉じると再表示できません）。
3. GitHub のリポジトリ → Settings → Secrets and variables → Actions → New repository secret
   - Name: `ANTHROPIC_API_KEY`、Secret: コピーしたキー
4. 一時停止したいときは、同じ画面の Variables に `JA_AUTOPUBLISH` = `false` を作ります（生成だけ止まり、サイトの再ビルドは続きます）。

## ステップ6: 初回実行と事実確認の結果チェック

1. リポジトリの Actions → `japan-affiliate-publish` → Run workflow。
2. 実行ログの「Verify facts against official pages」の出力（Summary）を見ます。
   - `OK` の項目は、公式ページに数値や文言が実際にあったことを自動で確認できたものです。
   - `FAIL` の項目は、**その事実を使う記事が公開されません**。原因は、公式ページの記載が変わった、URLが変わった、または私が引用した文字列が実際のページと違う、のいずれかです。公式ページを開いて確認し、`data/facts.json` の `source_url` と `must_contain` を直してください。直し方が分からなければ、そのログをClaudeに渡してください。
3. 2026-10-20 にこの環境で実際に公式ページと照合し、全23件が OK になりました。ただし、公式ページの内容は変わるため、あなたの実行でも FAIL が出ることがあります。FAIL は安全装置が働いた結果で、不具合ではありません。なお JR東日本（jreast.co.jp）のサイトは、自動アクセスを拒否する設定のため、この環境からは確認できませんでした。そのため JR東日本のページを根拠にする事実は、記事から外しています。GitHub 上の実行環境でも同様に拒否される可能性があります。
4. 成功すると、写真（Wikimedia Commons、クレジット付き）が取得され、サイトが公開されます。

## ステップ7: Search Console

公式: [Add a property](https://support.google.com/webmasters/answer/34592?hl=en)、[Verify ownership](https://support.google.com/webmasters/answer/9008080?hl=en)、[Sitemaps report](https://support.google.com/webmasters/answer/7451001?hl=en)

1. Search Console で「プロパティを追加」→ ドメインを選びます。
2. 表示された TXT レコードを Cloudflare の DNS に追加し、確認します。確認後に TXT レコードを消さないでください（公式の注意）。
3. 「サイトマップ」に `https://あなたのドメイン/sitemap.xml` を入力して送信します。送信は検索エンジンへのヒントで、取り込みの保証ではありません（公式の記載）。

## ステップ8: アフィリエイト登録（この順番で）

**先に訂正します。** 以前「最初は Travelpayouts が早い」とお伝えしましたが、公式のサポート記事では、Travelpayouts のウェブサイト審査の目安は「**月1,000アクティブユーザー以上**」で、旅行コンテンツが定期的に更新されていることが必要です。[出典: Travelpayouts サポート](https://support.travelpayouts.com/hc/en-us/articles/12865117818002-Why-was-my-request-to-connect-to-the-program-declined-)。公開直後は条件を満たさない可能性が高いため、順番を変えました。

共通の準備: 公開済みのサイトURL、記事が5本以上、プライバシーページ、連絡先、受け取り用の銀行口座またはPayPal（プログラムごとに異なります）。

| 順 | プログラム | 申込先（公式） | 公式に確認できた内容 | 貼る先（`config/affiliates.json`） |
|---|---|---|---|---|
| 1 | Agoda | [Agoda Partners](https://partners.agoda.com/en-us/faq.html) | 公開済みのサイトが必要（URLの転送だけは禁止）。登録後に審査があり、書面での承認で契約が有効になる。参加は無料 | `agoda` |
| 2 | Airalo（eSIM） | [Airalo Affiliate Program](https://www.airalo.com/m/resources/airalo-affiliate-program/) | Impact経由で申請。参加無料。標準料率は10%（公式ページの記載）。支払いは銀行またはPayPal | `esim` |
| 3 | Klook | [Klook Affiliate](https://affiliate.klook.com/home) | ウェブサイト向けの提携プログラム。詳細な審査条件は申込ページで確認 | `klook` |
| 4 | Booking.com | [Affiliate Partner Programme](https://partnerships.booking.com/) | 無料。登録は提携ネットワーク（CJ）経由。審査条件は申込ページで確認 | `booking` |
| 5 | Travelpayouts | [How to join](https://support.travelpayouts.com/hc/en-us/articles/11395179019538-How-to-join-Travelpayouts) | プロジェクト（サイト）を登録し所有確認が必要。目安は月1,000アクティブユーザー。Booking.comは審査が厳しいと明記 | 取れたプログラムを該当キーに |

- 鉄道パス（`railpass`）とポケットWiFi（`wifi`）は、**公式の提携窓口をまだ確認できていません**。見つかるまでリンクは空のまま（文字だけの表示）にしておきます。確認できていない提携先を、推測で登録しないでください。
- Viator、GetYourGuide（`viator`、`gyg`）も、公式の申込条件は未確認です。記事では使っていないため、必要になった時点で調べます。
- 提携先によって、サイトの審査に落ちることがあります。理由は申込先の案内に従い、記事を増やして再申請してください。

## ステップ9: 提携リンクを貼る

1. 承認されたら、提携先の管理画面で自分用のトラッキングリンク（あなたのIDが入ったURL）を取得します。
2. `config/affiliates.json` を開き、該当プログラムの `"link": ""` にそのURLを貼ります。
   - 例: `"agoda": {"name": "Agoda", ..., "link": "https://（Agodaの管理画面で取得したURL）", ...}`
   - 現在の仕組みでは、そのプログラムを使うすべての箇所が同じリンク（トップページ向けなど）になります。記事ごとの個別リンクには未対応です。必要なら、後で対応します。
3. コミットして main に反映すると、次回のワークフロー実行でサイトに反映されます。すぐに反映したいときは Actions から手動実行します。
4. 外部リンクには `rel="sponsored nofollow"` が自動で付きます。
5. 各社の規約に、広告であることの表示（開示）ルールがあります。サイトの全ページに開示文を出していますが、各社の最新の規約を確認してください。

## ステップ10: 運用

- **毎週**（15分）: Actions の Summary で `FAIL` の事実がないか、Search Console のカバレッジと検索パフォーマンスを確認します。
- **毎月**: 提携先の管理画面で、クリック数と成約を確認し、成果が出ている記事の分類を増やします。
- **記事の追加**: `data/topics.json` の優先度順に、毎日1本ずつ自動で作られます。トピックを足すのも同じファイルです。
- **事実の鮮度**: 各事実は90日以内に再確認されていないと、その事実を使う記事は再公開されません（安全装置）。毎日自動で再確認します。

## 税金（収益が出たら）

国税庁の案内によると、給与所得者で給与以外の所得が年間20万円を超える場合は確定申告が必要です（20万円は収入ではなく、収入から経費を引いた所得で判断）。アフィリエイトは、原則として事業所得または雑所得（業務）の対象とされています。
[No.1900 給与所得者で確定申告が必要な人](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1900.htm)、[No.1500 雑所得](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1500.htm)、[こんな収入の申告漏れにご注意](https://www.nta.go.jp/taxes/shiraberu/shinkoku/tokushu/shinkoku-tyuui/)
海外の提携先からの収入の扱いなど、個別の判断は税理士に確認してください。

## 広告（ディスプレイ広告）は後で

アクセスが育ってから、各社の公式ページで最新の参加条件を確認して申請します。今は不要です。

## 困ったとき

| 症状 | まず確認すること |
|---|---|
| 本番ビルドが止まる | ログの1行目のエラー文（`contact_email` 未設定、事実の未検証、写真の欠落など）が理由を示しています |
| 記事が増えない | Actions の実行結果、`ANTHROPIC_API_KEY`、`JA_AUTOPUBLISH` の値 |
| 写真が出ない | `pipeline.fetch_images` のログ（ライセンスに合う写真がなかった場合は取得されません） |
| 提携先に落ちた | 申込先の案内、記事数とプライバシーページの有無 |
