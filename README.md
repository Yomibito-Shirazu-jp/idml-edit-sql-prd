# idml-edit-sql-prd

IDMLの組版構造を固定し、Word原稿の「触ってよい本文領域」だけをSQLite台帳で管理して、IDMLへ安全に流し込むための制作パイプラインです。

## 目的

- InDesign/IDMLのスタイル、フレーム、ページ、マスター、柱、ノンブルを壊さない
- Word原稿の本文・座談会・脚注をSQLiteへ取り込み、版差分を追跡する
- 作業者AIや人間には `text` だけを編集させる
- IDML側は `Stories/*.xml` の原稿スロットだけを置換する
- GitHub Actionsで検証・成果物生成・必要に応じた自動commitを行う

## 基本フロー

```text
Word原稿(docx)
  -> SQLite blocks
IDMLテンプレート(idml)
  -> SQLite idml_slots
blocks <-> slots mapping
  -> touch_only CSV
  -> generated IDML
  -> PDF書き出しはInDesign/自社環境で実行
```

## 最小実行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python scripts/import_docx_to_sql.py --docx input/docx/main.docx --doc-type main --version v1 --db data/workflow.sqlite
python scripts/import_docx_to_sql.py --docx input/docx/talk.docx --doc-type roundtable --version v1 --db data/workflow.sqlite
python scripts/import_idml_to_sql.py --idml input/idml/template.idml --template-id template_v1 --db data/workflow.sqlite
python scripts/export_touch_only_csv.py --db data/workflow.sqlite --out output/reports/touch_only.csv
python scripts/validate_workflow.py --db data/workflow.sqlite --out output/reports/qa_report.md
```

## PDFについて

GitHub-hosted Ubuntu runnerにはInDesignがないため、このリポジトリの標準ActionsではPDFを直接書き出しません。PDF生成まで自動化する場合は、InDesignまたはInDesign Serverを持つself-hosted runnerを追加し、`.github/workflows/render-pdf-self-hosted.yml` を有効化してください。
