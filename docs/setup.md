# Setup Guide / 初期設定ガイド

![Setup flow](assets/setup-flow.svg)

## 1. Local environment / ローカル環境

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## 2. Purchase plan / 購入計画

`sample_data/purchase_plan.json` をコピーして、顧客ごとの名前・住所・数量割当を編集します。

English: Copy `sample_data/purchase_plan.json` and edit product identifiers, customer names, shipping addresses, and quantity allocations.

重要な入力項目:

| Field | Japanese | English |
|---|---|---|
| `asin` | 商品ASIN | Product ASIN |
| `buying_option_identifier` | Product Search APIまたはCart APIから得る購入オプション | Buying option from Product Search API or Cart API |
| `recipient_name` | 顧客名・受取人名 | Customer / recipient name |
| `external_address_id` | 自社側の住所ID | Your internal address ID |
| `buying_group_reference` | Amazon BusinessのBuying Group参照 | Amazon Business Buying Group reference |
| `payment_method_reference` | 支払い方法参照 | Payment method reference |
| `buyer_reference` | 購入者参照 | Buyer reference |

## 3. Generate files / ファイル生成

```bash
purchase-prep validate --input sample_data/purchase_plan.json
purchase-prep export --input sample_data/purchase_plan.json --output outputs
purchase-prep business-cart-payload --input sample_data/purchase_plan.json --output outputs/cart-add-items.json
purchase-prep business-order-payload --input sample_data/purchase_plan.json --recipient-label customer-a --output outputs/order-payload.json
```

## 4. Amazon Business settings / Amazon Business側の設定

![Amazon Business API flow](assets/amazon-business-api-flow.svg)

Amazon Business側で必要になる代表的な設定です。

English: The following values normally come from Amazon Business onboarding, Solution Provider Portal, Login with Amazon authorization, group configuration, and organization purchasing setup.

1. Amazon Business account
2. Developer registration / Solution Provider Portal app client
3. Login with Amazon OAuth client ID and client secret
4. Refresh token from authorization
5. API roles for Cart API / Ordering API
6. Buying Group reference
7. Payment method reference
8. Buyer reference
9. Customer shipping addresses or external address IDs
10. Region endpoint, for example `https://fe.business-api.amazon.com` for JP-oriented FE workflows

## 5. Environment variables / 環境変数

```bash
cp .env.example .env
```

`.env` の値はGitHubにcommitしません。GitHub Actionsで使う場合はSecretsに同じ名前で登録します。

Required:

```bash
AMAZON_BUSINESS_CLIENT_ID=...
AMAZON_BUSINESS_CLIENT_SECRET=...
AMAZON_BUSINESS_REFRESH_TOKEN=...
AMAZON_BUSINESS_REGION=JP
AMAZON_BUSINESS_BASE_URL=https://fe.business-api.amazon.com
AMAZON_BUSINESS_BUYER_EMAIL=buyer@example.co.jp
AMAZON_BUSINESS_USER_AGENT="AmazonBusinessPurchaseAutomationAssistant/0.2.0 (Language=Python/3.11)"
```

Optional:

```bash
AMAZON_BUSINESS_BUYING_GROUP_REFERENCE=...
AMAZON_BUSINESS_PAYMENT_METHOD_REFERENCE=...
AMAZON_BUSINESS_BUYER_REFERENCE=...
```

## 6. Live API commands / API接続コマンド

```bash
purchase-prep business-list-carts --region JP --live
purchase-prep business-add-items --input sample_data/purchase_plan.json --cart-id cart-123 --region JP --live
purchase-prep business-place-order --payload outputs/order-payload.json --live
```

## 7. Codespaces

GitHubで `Code` → `Codespaces` → `Create codespace on main` を選ぶと、devcontainerがPython環境と依存関係をセットアップします。

English: Open the repository in GitHub Codespaces to get a preconfigured Python development environment.
