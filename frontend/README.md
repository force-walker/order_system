# frontend

受注管理MVPのフロントエンド（React + Vite + TypeScript）

## 実装済み（mock）
- 受注一覧 `/orders`
- 受注詳細 `/orders/:id`
- 受注作成 `/orders/new`
- 受注編集 `/orders/:id/edit`
- 状態UI: loading / empty / error / success
- バリデーション: 顧客名必須・金額>0

## 起動
```bash
npm install
npm run dev
```

## モックAPIの挙動
- 一覧検索で `error` を入力するとエラー状態
- 顧客名に `error` を入力して保存すると保存エラー
