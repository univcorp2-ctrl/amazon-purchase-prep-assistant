# CODEX.md

## 開発方針

このプロジェクトは、購入準備と手動確認の効率化だけを対象にします。Amazonのウェブ画面をブラウザ自動操作するコード、チェックアウト到達コード、住所フォーム自動入力、CAPTCHA/2FA回避、ブロック回避、人間風挙動、プロキシローテーション、ステルスブラウザ設定は追加しないでください。

## 推奨する拡張

- Amazon Business公式APIの認可済みsandboxクライアント
- 社内承認フローとの連携
- 購入候補の重複検知
- 予算上限・数量上限の検証
- CSV/Excel出力フォーマットの追加

## テスト

```bash
ruff check .
pytest
purchase-prep export --input sample_data/purchase_plan.json --output outputs
```
