# GPT-Image 2 Visual Guide / 画像生成ガイド

このファイルは、READMEとdocsのSVG図をGPT-Image 2の最新モデルで高解像度の説明画像に変換するためのプロンプト集です。

English: This file contains prompts for regenerating the repository diagrams as high-resolution explanatory images with the latest GPT-Image 2 model.

## 1. Architecture overview / 全体設計図

Prompt:

> Create a clean bilingual Japanese-English technical architecture diagram for an Amazon Business purchase automation assistant. Show purchase_plan.json feeding Pydantic models, validation, exporters, Cart API payload builder, Ordering API payload builder, Login with Amazon token exchange, Amazon Business Cart API, and Amazon Business Ordering API. Use blue and orange enterprise colors, rounded boxes, arrows, and small icons. Include Japanese labels first and English subtitles under each label. 16:9, high resolution, presentation ready.

## 2. Procedure flow / 処理の流れ

Prompt:

> Create a step-by-step procedure flow diagram in Japanese and English. Steps: 1 edit purchase_plan.json, 2 validate, 3 generate CSV Excel TXT JSON, 4 configure .env / GitHub Secrets, 5 list carts, 6 add items to cart, 7 generate order payload, 8 place order with Ordering API. Use numbered lanes, calm colors, clear arrows, and beginner-friendly annotations. 16:9.

## 3. Script roles / 各スクリプトの役割

Prompt:

> Create a bilingual script role map for a Python repository. Files: models.py, parsers.py, safety.py, business_payloads.py, business_api.py, exporters.py, cli.py, api.py, tests. Show each as a file card with role, input, and output. Use Japanese title and English subtitle. Technical but easy to understand. 16:9.

## 4. Amazon Business API flow / API連携図

Prompt:

> Create a detailed Amazon Business API integration flow diagram. Show environment variables, Login with Amazon refresh token exchange, x-amz-access-token header, Cart API listCarts/addItems/getItems/estimateTotalPurchaseCost, Ordering API placeOrder/orderDetails, and customer address payload. Bilingual Japanese-English labels. Use secure enterprise style, blue/orange palette, clear sequence arrows. 16:9.

## 5. Setup guide / 初期設定ガイド

Prompt:

> Create a beginner-friendly setup guide image in Japanese and English for configuring an Amazon Business API integration. Show local Python setup, .env.example copy, Amazon Business Solution Provider Portal values, GitHub Actions Secrets, purchase_plan.json editing, and CLI commands. Use visual checkmarks, numbered steps, and soft colors. 16:9.

## 6. Data model / データ構造

Prompt:

> Create a data model diagram for Amazon Business purchase automation. Entities: PurchasePlan, ProductItem, RecipientProfile, Allocation, CartAddItemsPayload, OrderingPayload. Show important fields such as asin, buying_option_identifier, quantity, recipient_name, postal_code, buying_group_reference, payment_method_reference, lineItems, attributes, expectations. Bilingual Japanese-English labels. 16:9.
