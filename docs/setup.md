# Setup Guide

## 1. ローカル実行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
purchase-prep validate --input sample_data/purchase_plan.json
purchase-prep export --input sample_data/purchase_plan.json --output outputs
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
purchase-prep validate --input sample_data/purchase_plan.json
purchase-prep export --input sample_data/purchase_plan.json --output outputs
```

## 2. Codespaces

GitHub上で `Code` → `Codespaces` → `Create codespace on main` を選ぶと、devcontainerがPython環境と依存関係をセットアップします。

## 3. GitHub Actions artifact

1. GitHubのActionsタブを開く
2. `CI` workflowを選ぶ
3. `Run workflow` を押す
4. 完了後、`purchase-prep-outputs` artifactをダウンロードする

## 4. Amazon Business公式APIを使う場合

個人向けAmazon.co.jp画面のブラウザ自動化ではなく、Amazon Businessの公式API利用を検討してください。

必要になる代表的な設定:

- Amazon Businessアカウント
- Solution Provider Portalでのアプリ登録
- Login with Amazon / OAuthトークン
- Amazon Business APIロール
- Buying Group参照
- 組織の支払い方法と配送先
- 購買承認ルール

実シークレット値はGitHubへコミットしないでください。GitHub Actions Secretsを使う場合の名前例:

- `AMAZON_BUSINESS_CLIENT_ID`
- `AMAZON_BUSINESS_CLIENT_SECRET`
- `AMAZON_BUSINESS_REFRESH_TOKEN`
- `AMAZON_BUSINESS_BUYING_GROUP_ID`

## 5. 本番運用の境界

このリポジトリ単体で本番購入は行いません。本番購入を自動化するには、Amazon Business APIの利用承認、組織側の購買設定、監査ログ、承認フロー、権限管理が必要です。
