# Amazon Business API Research / 公式API調査

## Summary / 要約

Amazon Businessには、購入システムから公式にカート管理・注文作成を行うAPIがあります。本リポジトリでは、Cart APIとOrdering APIのpayload生成、LWA token exchange、公式API HTTP client、CLIを実装しました。

English: Amazon Business provides official APIs for cart management and ordering. This repository implements payload builders, Login with Amazon token exchange, a thin official API HTTP client, and CLI commands.

## Cart API

Cart API operations include:

- `GET /cart/2025-04-30/carts`
- `GET /cart/2025-04-30/carts/{cartId}`
- `GET /cart/2025-04-30/carts/{cartId}/items`
- `POST /cart/2025-04-30/carts/{cartId}/items`
- `PATCH /cart/2025-04-30/carts/{cartId}/items`
- `DELETE /cart/2025-04-30/carts/{cartId}/items`
- `POST /cart/2025-04-30/carts/{cartId}/totalPurchaseCostEstimations`

Implementation:

- `business_payloads.build_cart_add_items_payload()`
- `AmazonBusinessClient.list_carts()`
- `AmazonBusinessClient.add_items()`
- `AmazonBusinessClient.get_items()`
- `AmazonBusinessClient.estimate_total_purchase_cost()`

## Ordering API

Ordering API operations include:

- `POST /ordering/2022-10-30/orders`
- `GET /ordering/2022-10-30/orders/{externalId}`

Implementation:

- `business_payloads.build_order_payload()`
- `AmazonBusinessClient.place_order()`
- `AmazonBusinessClient.order_details()`

## MCP

Amazon Business公式の `amazonbusiness/ab-integrations-mcp-server` は、AI開発環境からAmazon Business APIドキュメント、サンプルコード、トラブルシューティング情報を検索・参照するためのMCPです。

English: The official `amazonbusiness/ab-integrations-mcp-server` helps AI-enabled developer environments access Amazon Business API documentation, sample code, and troubleshooting references.

## Data needed from Amazon Business / Amazon Business側から取得する値

- Client ID
- Client secret
- Refresh token
- Region / marketplace
- API base URL
- Buyer email
- Buying Group reference
- Payment Method reference
- Buyer reference
- ASIN and buyingOptionIdentifier for each line item

## Implementation map / 実装対応表

| Official area | Repository file | CLI |
|---|---|---|
| LWA token | `business_api.py` | all `business-* --live` commands |
| Cart API addItems | `business_api.py`, `business_payloads.py` | `business-add-items` |
| Cart API listCarts | `business_api.py` | `business-list-carts` |
| Ordering API placeOrder | `business_api.py`, `business_payloads.py` | `business-place-order` |
| Address payload | `business_payloads.py` | `business-order-payload` |
