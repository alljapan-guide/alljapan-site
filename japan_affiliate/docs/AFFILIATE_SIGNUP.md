# アフィリエイト登録手順（Agoda 以外）

登録はご本人の名前・口座・税情報・規約同意が必要なため、**ご自身の操作**になります。承認後に届く「提携リンク」を私に貼っていただければ、`config/affiliates.json` に入れて公開まで行います（リンクは秘密情報ではありません。**パスワードやAPIキーは貼らないでください**）。

出典の注記：条件・手数料はネットワークや時期で変わります。下記は検索で確認できた範囲で、**必ず各社の公式画面で最新条件を確認してください**。

## 共通の準備（先に済ませる）
- サイトURL：https://alljapan.win （記事は現在11本。多いほど審査に通りやすい傾向ですが、各社の公式基準は未確認）
- 連絡先：all.japan00guide@gmail.com
- サイト説明（そのまま使えます。事実のみ）：
  > All Japan is an English-language travel guide for first-time visitors to Japan. Each article cites official tourism sources (JNTO, GO TOKYO, Kyoto City Tourism Association and others) and includes diagrams and licensed photos. Topics: transport, hotels, itineraries, connectivity, culture and food. Traffic plan: organic search.
- 申請欄に「AIは使っていない」とは書かない。記事の作成にAIを使っている事実を隠さないこと（質問された場合は正直に答える）。
- 支払い・税情報は各ネットワークの画面でご本人が入力。

## 登録の順番
1. **Airalo（eSIM）**：Impact 経由。公式ページ https://www.airalo.com/m/resources/airalo-affiliate-program から申請。手数料は公式FAQで10%〜と記載（要・最新確認）。記事：japan-esim-vs-pocket-wifi。リンク → `esim`
2. **Klook**：公式の提携案内から申請（ネットワーク経由の場合あり。手数料は情報源で食い違うため公式画面で確認）。リンク → `klook`
3. **Booking.com**：地域によりネットワークが異なる（CJ または Awin と案内されることが多い）。Booking.com のパートナー案内から、日本向けの申込先を選ぶ。リンク → `booking`
4. **Travelpayouts**：月間訪問者の目安が約1,000人（過去の確認時点）。アクセスが増えてから。
5. 未確認のため後回し：Japan Rail Pass 販売会社、ポケットWiFi、Viator、GetYourGuide（公式の提携プログラムを私が確認できたら案内します）。

## 承認後にやること
1. 各社の管理画面で「トラッキングリンク」を発行（サイト全体用の1本で可）。
2. そのURLを私に貼る（どのプログラムのリンクかも書く）。
3. 私が `config/affiliates.json` の該当 `link` に入れ、ビルド・公開する。
4. 記事内の該当テキストが自動でリンクになり、リンクがない間は通常のテキストのままです。
5. 開示文（アフィリエイトリンクを含む旨）は全記事とフッターに表示済みです。
