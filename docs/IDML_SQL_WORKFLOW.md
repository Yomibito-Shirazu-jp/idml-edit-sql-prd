# IDML-SQL Workflow Design

## 触ってよい場所

このパイプラインで編集してよいのは、原則としてDBの `blocks.text` のみです。

- `TEXT_ONLY_REPLACE`: 本文・見出し・座談会本文の文字列のみ置換可
- `FOOTNOTE_TEXT_ONLY_REPLACE_ANCHOR_LOCKED`: 脚注本文のみ置換可。脚注アンカーは固定

## 触ってはいけない場所

- `Resources/Styles.xml`
- `Resources/Fonts.xml`
- `Spreads/*.xml`
- `MasterSpreads/*.xml`
- `designmap.xml`
- フレーム位置、ページ構造、柱、ノンブル、マスター

## DBを正本にする理由

CSVは編集ビューです。正本はSQLiteです。DBには、Word側の段落、IDML側のスロット、対応関係、検証結果を蓄積します。

```text
documents -> blocks -> block_slot_map -> idml_slots
```

## 変数化IDMLの考え方

IDMLの `Stories/*.xml` だけを対象に、本文の差し込み箇所を `{{P_000001}}` のようなスロットにします。生成時はDBの `blocks.text` をXMLエスケープしてスロットへ流し込みます。

## 推奨運用

1. Word原稿をDBへimport
2. IDMLテンプレートからslot候補をDBへimport
3. mappingを確認
4. touch_only CSVを出力
5. CSVまたはDBのtextだけ修正
6. generated IDMLを作成
7. InDesignでPDFを書き出し
8. PDF検収結果をDBまたはreportへ戻す
