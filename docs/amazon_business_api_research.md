# Amazon Business API / MCP Research

## 公式APIの方向性

Amazon Businessには、外部購買システムと連携するための公式APIがあります。個人向けAmazonのブラウザ画面をRPAで動かすより、法人購買では公式APIを使う設計が安全です。

## Cart API

Cart APIは、Amazon Businessのカートを外部システムから作成・変更・取得し、税金や送料を含む見積りを扱うためのAPIです。ASINとoffer IDはProduct Search APIから取得する前提です。

このリポジトリでは実API呼び出しは行わず、`*-amazon-business-template.json` にdry-runテンプレートだけを出力します。

## Ordering API

Ordering APIは、Amazon Businessの購入注文を外部購買システムから送信するためのAPIです。OAuth / Login with Amazon、Buying Group、支払い方法、配送先、承認ルールなどの事前設定が必要です。

## MCP

Amazon Business公式の `ab-integrations-mcp-server` は、Amazon Business APIドキュメント、サンプルコード、トラブルシューティング情報へAI開発環境からアクセスするためのMCPです。購入画面を操作するMCPではなく、公式API統合を支援するためのものです。

## 本ツールで採用した範囲

- 購入計画JSONの検証
- URL/ASINの静的解析
- CSV/Excel/TXT/APIテンプレート生成
- GitHub Actions artifact出力

## 採用しない範囲

- Chrome/Playwright/SeleniumでAmazon画面を操作する実装
- カート投入・購入確認画面遷移・購入確定
- 住所フォームの自動入力
- CAPTCHA/2FA/ブロック回避
- Amazon画面変更パターンの自動探索
