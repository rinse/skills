# 外部リソースとライセンス

デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/ のコンテンツを加工して作成。
出典：https://design.digital.go.jp/dads/resources/ 、https://design.digital.go.jp/dads/introduction/notices/ 、https://design.digital.go.jp/dads/guidance/accessibility/

## DADS が提供するもの

| リソース | 場所 | ライセンス |
| --- | --- | --- |
| デザインシステム本体（このサイトの文書、ガイドライン） | https://design.digital.go.jp/dads/ | デジタル庁ウェブサイトのコピーライトポリシー（出典の記載が必要） |
| ドキュメント（Markdown） | https://design.digital.go.jp/dads/resources/ から最新の zip | 本体と同じ |
| デザインデータ（Figma） | https://www.figma.com/community/file/1377880368787735577 | CC BY 4.0（一部の Material Symbols は Apache License 2.0） |
| コードスニペット（HTML 版） | [GitHub](https://github.com/digital-go-jp/design-system-example-components-html)、[Storybook](https://design.digital.go.jp/dads/html/) | MIT License |
| コードスニペット（React 版） | [GitHub](https://github.com/digital-go-jp/design-system-example-components-react)、[Storybook](https://design.digital.go.jp/dads/react/) | MIT License |
| デザイントークン | [GitHub](https://github.com/digital-go-jp/design-tokens)、npm `@digital-go-jp/design-tokens` | MIT License |
| Tailwind CSS テーマプラグイン | [GitHub](https://github.com/digital-go-jp/tailwind-theme-plugin)、npm `@digital-go-jp/tailwind-theme-plugin` | MIT License |
| イラストレーション・アイコン素材 | https://www.digital.go.jp/policies/servicedesign/designsystem/Illustration_Icons | [利用規約](https://www.digital.go.jp/policies/servicedesign/designsystem/Illustration_Icons/terms_of_use)の範囲で無料 |

- ドキュメント（Markdown）はサイト全体を AI 参照向けに変換したもので、各ファイルの frontmatter に `source_url` がある。完全な内容は公式ページで確認する。
- コードスニペットは実装のサンプル。利用環境やフレームワークに合わせて書き換えてよいが、WAI-ARIA の指定や強制カラーモード対応は取り除かない。導入方法と各コンポーネントの仕組みは Storybook に解説がある。
- Figma データのコンポーネント構成は状態の組み合わせを示すためのもの。使い方に合わなければ detach して組み直し、ローカルデザインシステムのコンポーネントとして定義し直してよい。
- 調達仕様書の記載時点など、特定バージョンの DADS が必要な場合はデジタル庁の問い合わせ窓口に依頼する。

## 出典の記載

- **本体のコンテンツを使う場合**：「出典：デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/」と記載する。
- **本体を編集・加工して使う場合**：上とは別に加工したことを記載する（例：「デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/ のコンテンツを加工して作成」）。加工した情報を、デジタル庁が作成したかのような態様で公表しない。
- **Figma データとコードスニペット**：編集・加工して作った画面パーツをサイトで使う場合、出典の明記は不要。加工せずに公開する場合は出典を記載する。

## アクセシビリティの基準と参考資料

- [WCAG 2.2 日本語訳（WAIC）](https://waic.jp/translations/WCAG22/)：DADS が参照する最新の勧告。各達成基準の解説書も WAIC にある。
- JIS X 8341-3:2016：WCAG 2.0 と同一内容の国内規格。DADS のバッジ「JIS2016」はこれに含まれる達成基準を示す。
- [WAI-ARIA 1.2](https://www.w3.org/TR/wai-aria-1.2/)、[ARIA Authoring Practices Guide（APG）](https://www.w3.org/WAI/ARIA/apg/)：独自のウィジェットを実装するときのロール、状態、キーボード操作のパターン。
- [デジタル庁ウェブアクセシビリティ導入ガイドブック](https://www.digital.go.jp/resources/introduction-to-web-accessibility-guidebook)：アクセシビリティに初めて取り組む行政官や事業者向けの入門。
- [カラーユニバーサルデザイン推奨配色セット](https://jfly.uni-koeln.de/colorset/)：キーカラーなどのパレットを選ぶときの参考。
- [HTML Standard](https://html.spec.whatwg.org/multipage/)、[CSS](https://www.w3.org/Style/CSS/)。
- 改正障害者差別解消法（2024 年 4 月 1 日施行）は、合理的配慮に先立つ環境の整備を努力義務としており、ウェブアクセシビリティの確保がこれにあたる。
