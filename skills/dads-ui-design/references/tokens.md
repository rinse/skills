# デザイントークンと基本の CSS

デジタル庁デザインシステムウェブサイト https://design.digital.go.jp/dads/ のコンテンツを加工して作成。
トークンの値は [digital-go-jp/design-tokens](https://github.com/digital-go-jp/design-tokens) の `examples/tokens.css`（MIT License、2026-05-28 時点の HEAD）から、CSS は [digital-go-jp/design-system-example-components-html](https://github.com/digital-go-jp/design-system-example-components-html) の `src/global.css` と `src/components/button/button.css`（MIT License）から転記した。
リポジトリの README が対応を明記している Figma データは 2.14.0 までで、2.18.0 と値が完全に一致する保証はない。厳密な値が必要なときは Figma データか npm パッケージの最新版を確認する。

## 導入

- CSS：`npm install @digital-go-jp/design-tokens` で `tokens.css`（全トークン）と `tokens-simple.css`（色、フォント、エレベーションのみ）が入る。
- Tailwind CSS：`npm install @digital-go-jp/tailwind-theme-plugin`。v4 は `@import '@digital-go-jp/tailwind-theme-plugin/v4';`、v3 は `plugins: [require('@digital-go-jp/tailwind-theme-plugin')]`。

## カラー

### プリミティブカラー（`--color-primitive-<色相>-<段階>`）

| 段階 | blue | light-blue | cyan | green | lime | yellow | orange | red | magenta | purple |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 50 | `#e8f1fe` | `#f0f9ff` | `#e9f7f9` | `#e6f5ec` | `#ebfad9` | `#fbf5e0` | `#ffeee2` | `#fdeeee` | `#f3e5f4` | `#f1eafa` |
| 100 | `#d9e6ff` | `#dcf0ff` | `#c8f8ff` | `#c2e5d1` | `#d0f5a2` | `#fff0b3` | `#ffdfca` | `#ffdada` | `#ffd0ff` | `#ecddff` |
| 200 | `#c5d7fb` | `#c0e4ff` | `#99f2ff` | `#9bd4b5` | `#c0f354` | `#ffe380` | `#ffc199` | `#ffbbbb` | `#ffaeff` | `#ddc2ff` |
| 300 | `#9db7f9` | `#97d3ff` | `#79e2f2` | `#71c598` | `#ade830` | `#ffd43d` | `#ffa66d` | `#ff9696` | `#ff8eff` | `#cda6ff` |
| 400 | `#7096f8` | `#57b8ff` | `#2bc8e4` | `#51b883` | `#9ddd15` | `#ffc700` | `#ff8d44` | `#ff7171` | `#f661f6` | `#bb87ff` |
| 500 | `#4979f5` | `#39abff` | `#01b7d6` | `#2cac6e` | `#8cc80c` | `#ebb700` | `#ff7628` | `#ff5454` | `#f137f1` | `#a565f8` |
| 600 | `#3460fb` | `#008bf2` | `#00a3bf` | `#259d63` | `#7eb40d` | `#d2a400` | `#fb5b01` | `#fe3939` | `#db00db` | `#8843e1` |
| 700 | `#264af4` | `#0877d7` | `#008da6` | `#1d8b56` | `#6fa104` | `#b78f00` | `#e25100` | `#fa0000` | `#c000c0` | `#6f23d0` |
| 800 | `#0031d8` | `#0066be` | `#008299` | `#197a4b` | `#618e00` | `#a58000` | `#c74700` | `#ec0000` | `#aa00aa` | `#5c10be` |
| 900 | `#0017c1` | `#0055ad` | `#006f83` | `#115a36` | `#507500` | `#927200` | `#ac3e00` | `#ce0000` | `#8b008b` | `#5109ad` |
| 1000 | `#00118f` | `#00428c` | `#006173` | `#0c472a` | `#3e5a00` | `#806300` | `#8b3200` | `#a90000` | `#6c006c` | `#41048e` |
| 1100 | `#000071` | `#00316a` | `#004c59` | `#08351f` | `#2c4100` | `#6e5600` | `#6d2700` | `#850000` | `#500050` | `#30016c` |
| 1200 | `#000060` | `#00234b` | `#003741` | `#032213` | `#1e2d00` | `#604b00` | `#541e00` | `#620000` | `#3b003b` | `#21004b` |

### ニュートラルカラー

`--color-neutral-white: #ffffff`、`--color-neutral-black: #000000`。
グレーは HEX の Solid Gray（`--color-neutral-solid-gray-<段階>`）と、黒の透過度による Opacity Gray（`--color-neutral-opacity-gray-<段階>`）がある。

| 段階 | Solid Gray | Opacity Gray |
| --- | --- | --- |
| 50 | `#f2f2f2` | `rgba(0,0,0,0.05)` |
| 100 | `#e6e6e6` | `rgba(0,0,0,0.1)` |
| 200 | `#cccccc` | `rgba(0,0,0,0.2)` |
| 300 | `#b3b3b3` | `rgba(0,0,0,0.3)` |
| 400 | `#999999` | `rgba(0,0,0,0.4)` |
| 420 | `#949494` | `rgba(0,0,0,0.42)` |
| 500 | `#7f7f7f` | `rgba(0,0,0,0.5)` |
| 536 | `#767676` | `rgba(0,0,0,0.54)` |
| 600 | `#666666` | `rgba(0,0,0,0.6)` |
| 700 | `#4d4d4d` | `rgba(0,0,0,0.7)` |
| 800 | `#333333` | `rgba(0,0,0,0.8)` |
| 900 | `#1a1a1a` | `rgba(0,0,0,0.9)` |

コントラストの境界：

- 白背景：Gray-420 より暗いグレーは非テキスト要件（3:1）を、Gray-536 より暗いグレーはテキスト要件（4.5:1）を満たす。
- 黒背景：Gray-600 より明るいグレーは非テキスト要件を、Gray-536 より明るいグレーはテキスト要件を満たす。

### キーカラーとセマンティックカラー

キーカラーは `--color-key-<段階>`（50〜1200）で、初期値は Blue の各段階を参照する。ローカルデザインシステムではこの参照先を差し替える。

| トークン | 参照先 |
| --- | --- |
| `--color-semantic-success-1` / `-2` | green-600 / green-800 |
| `--color-semantic-error-1` / `-2` | red-800 / red-900 |
| `--color-semantic-warning-yellow-1` / `-2` | yellow-700 / yellow-900 |
| `--color-semantic-warning-orange-1` / `-2` | orange-600 / orange-800 |

## タイポグラフィ

```css
--font-family-sans: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, sans-serif;
--font-family-mono: 'Noto Sans Mono', monospace;
--font-weight-400: 400;
--font-weight-700: 700;
```

- `--font-size-<px>`：14, 16, 17, 18, 20, 22, 24, 26, 28, 32, 36, 45, 48, 57, 64（値は `px / 16` の rem）。
- `--line-height-<%>`：100, 120, 130, 140, 150, 160, 170, 175（値は単位なしの数値。`--line-height-150: 1.5`）。
- テキストスタイルの組み合わせは [foundations.md](foundations.md) のタイポグラフィを参照。HTML 版スニペットは `.dads-u-std-16N-170` のようなユーティリティクラスとして定義している。

## 角の形状

`--border-radius-<px>`：4, 6, 8, 12, 16, 24, 32（rem 換算）と `--border-radius-full`（完全な角丸）。

## エレベーション

| トークン | 値 |
| --- | --- |
| `--elevation-1` | `0 2px 8px 1px rgba(0,0,0,0.1), 0 1px 5px 0 rgba(0,0,0,0.3)` |
| `--elevation-2` | `0 2px 12px 2px rgba(0,0,0,0.1), 0 1px 6px 0 rgba(0,0,0,0.3)` |
| `--elevation-3` | `0 4px 16px 3px rgba(0,0,0,0.1), 0 1px 6px 0 rgba(0,0,0,0.3)` |
| `--elevation-4` | `0 6px 20px 4px rgba(0,0,0,0.1), 0 2px 6px 0 rgba(0,0,0,0.3)` |
| `--elevation-5` | `0 8px 24px 5px rgba(0,0,0,0.1), 0 2px 10px 0 rgba(0,0,0,0.3)` |
| `--elevation-6` | `0 10px 30px 6px rgba(0,0,0,0.1), 0 3px 12px 0 rgba(0,0,0,0.3)` |
| `--elevation-7` | `0 12px 36px 7px rgba(0,0,0,0.1), 0 3px 14px 0 rgba(0,0,0,0.3)` |
| `--elevation-8` | `0 14px 40px 7px rgba(0,0,0,0.1), 0 3px 16px 0 rgba(0,0,0,0.3)` |

余白のトークンは提供されていない。8px を基準単位として導入先で定める（[foundations.md](foundations.md) の余白を参照）。

## フォーカスインジケーター

黒のアウトラインと Yellow-300 の二重構造。どの導入先でも変更しない。

```css
:focus-visible {
  outline: calc(4 / 16 * 1rem) solid var(--color-neutral-black);
  outline-offset: calc(2 / 16 * 1rem);
  border-radius: calc(4 / 16 * 1rem);
  box-shadow: 0 0 0 calc(2 / 16 * 1rem) var(--color-primitive-yellow-300);
}
```

## リンク

```css
:where(a):any-link {
  color: var(--color-primitive-blue-1000);
  text-decoration: underline;
  text-decoration-thickness: calc(1 / 16 * 1rem);
  text-underline-offset: calc(3 / 16 * 1rem);
}
:where(a):visited {
  color: var(--color-primitive-magenta-900);
}
@media (hover: hover) {
  :where(a):hover {
    color: var(--color-primitive-blue-900);
    text-decoration-thickness: calc(3 / 16 * 1rem);
  }
}
:where(a):active {
  color: var(--color-primitive-orange-800);
  text-decoration-thickness: calc(1 / 16 * 1rem);
}
```

## ボタンの色の割り当て（初期値）

| スタイル | default | hover | active | disabled |
| --- | --- | --- | --- | --- |
| 塗り | 背景 key-900、ラベル白 | 背景 key-1000 + 下線 | 背景 key-1200 + 下線 | 背景 solid-gray-300、ラベル solid-gray-50 |
| アウトライン | 枠とラベル key-900、背景白 | 背景 key-200 + 下線 | 背景 key-300 + 下線 | ラベル solid-gray-300 |
| テキスト | ラベル key-900 + 下線、背景透明 | 背景 key-50、ラベル key-1000、下線を太く | 背景 key-100、ラベル key-1200 | ラベル solid-gray-300 |

ラベルは 16px（X-Small のみ 14px）、太さ 700、行高 1、字間 0.02em。強制カラーモードでは disabled の枠とラベルを `GrayText` にする。

| サイズ | 最小幅 × 最小高さ | 角丸 | padding（上下 左右） |
| --- | --- | --- | --- |
| Large | 136 × 56px | 8px | 12px 16px |
| Medium | 96 × 48px | 8px | 8px 16px |
| Small | 80 × 36px | 6px | 2px 12px |
| X-Small | 72 × 28px | 4px | 2px 8px |

Small と X-Small は高さ 44px の疑似要素（`::after`）でターゲット領域を確保している。
