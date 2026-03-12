# 帳票 / API I/O 定義 Draft (MVP)

Updated: 2026-03-12

## 目的
- 画面・CSV・PDF・APIで使う項目名を統一
- 必須/任意、型、フォーマット、コード値を固定
- 実装とUATの判定基準にする

---

## 1) 共通ルール

- 数量/重量/金額は `numeric/decimal`（float禁止）
- 日付: `YYYY-MM-DD`
- 日時: ISO8601 (`YYYY-MM-DDTHH:mm:ssZ`)
- 仕入通貨: `JPY`
- 販売/請求通貨: `HKD`
- 真偽: `true/false`

コード値（MVP）:
- `order_uom_type`: `uom_count | uom_kg`
- `stockout_policy`: `backorder | substitute | cancel | partial_ok`
- `order_status`: `new | confirmed | purchasing | shipped | delivered | invoiced | cancelled`
- `result_status`: `full | partial | failed | substitute`

---

## 2) API I/O 定義（主要）

## 2.1 Create Order
- Endpoint: `POST /api/orders`

Request fields:
- `customer_id` (int, required)
- `order_datetime` (datetime, required)
- `delivery_type` (string, required)
- `delivery_date` (date, required)
- `delivery_note` (string, optional)
- `items[]` (required, min 1)
  - `product_id` (int, required)
  - `ordered_qty` (decimal(12,2), required, >0)
  - `order_uom_type` (`uom_count`|`uom_kg`, productから自動反映)
  - `estimated_weight_kg` (decimal(12,3), optional)
  - `price_ceiling` (decimal(12,2), optional)
  - `stockout_policy` (enum, optional)
  - `comment` (string, optional)

Notes:
- `pricing_basis` は `product_id` から自動決定（requestでは受け付けない）
- `unit_price_order_uom` / `unit_price_per_kg` は受注作成時には入力不要
- `actual_weight_kg` は受注作成時には入力しない（仕入結果登録時に確定）
- tax関連項目は受注時には扱わない（請求時に適用）

Response fields:
- `order_id` (int)
- `order_no` (string)
- `item_count` (int)

---

## 2.2 Allocation Override
- Endpoint: `PATCH /api/allocations/{allocation_id}/override`

Request fields:
- `final_supplier_id` (int, required)
- `final_qty` (decimal(12,3), required, >0)
- `final_uom` (string, required)
- `target_price` (decimal(12,2), optional)
- `stockout_policy` (enum, optional)
- `comment` (string, optional)
- `override_reason_code` (string, required)
- `override_note` (string, optional)
- `overridden_by` (string, required)

Response fields:
- `ok` (bool)
- `allocation_id` (int)

---

## 2.3 Allocation Split Line
- Endpoint: `POST /api/allocations/{allocation_id}/split-line`

Request fields:
- `parts[]` (required, min 2)
  - `final_supplier_id` (int, required)
  - `final_qty` (decimal(12,3), required)
  - `final_uom` (string, required)
- `override_reason_code` (required)
- `override_note` (optional)
- `overridden_by` (required)

Validation:
- `sum(parts.final_qty) == parent allocation qty`
- UOM consistency check

Response fields:
- `split_group_id` (string)
- `allocation_ids` (int[])

---

## 2.4 Purchase Result Registration
- Endpoint: `POST /api/purchase-results`（実装予定）

Request fields:
- `allocation_id` (int, required)
- `supplier_id` (int, required)
- `purchased_qty` (decimal(12,3), required)
- `purchased_uom` (string, required)
- `actual_weight_kg` (decimal(12,3), optional)
- `unit_cost` (decimal(12,2), optional)
- `final_unit_cost` (decimal(12,2), optional)
- `currency` (string(3), optional default JPY, purchase currency)
- `cost_uom` (string, optional)
- `result_status` (enum, required)
- `note` (optional)

Response fields:
- `purchase_result_id` (int)
- `result_status` (enum)

---

## 2.5 Invoice Create / Finalize
- Endpoints:
  - `POST /api/invoices`
  - `POST /api/invoices/{id}/finalize`

Create request fields:
- `order_id` (int, required)
- `invoice_no` (string, required)
- `invoice_date` (date, required)
- `delivery_date` (date, required)
- `currency` (string(3), default HKD)

Finalize hard-stops:
- catch-weight line missing `actual_weight_kg`
- required unit price missing
- negative total

Finalize response fields:
- `invoice_id` (int)
- `status` (`finalized`)
- `sales_unit_price` (decimal(12,2), required)
- `unit_cost_basis` (decimal(12,2), optional/internal)
- `gross_margin_rate` (decimal(8,4), optional/internal)

---

## 3) 帳票 I/O 定義

## 3.1 発注リスト（By Supplier）CSV
Filename example:
- `purchase_list_YYYYMMDD_supplier_<id>.csv`

Columns:
- `batch_id`
- `supplier_id`
- `supplier_name`
- `order_no`
- `customer_name`
- `product_sku`
- `product_name`
- `ordered_qty`（受注数量）
- `ordered_uom_type`
- `final_qty`（発注数量）
- `final_uom`
- `target_price`
- `stockout_policy`
- `comment`

---

## 3.2 納品/仕入結果入力用CSV（任意）
Columns:
- `allocation_id`
- `supplier_id`
- `purchased_qty`
- `purchased_uom`
- `actual_weight_kg`
- `unit_cost`
- `final_unit_cost`
- `result_status`
- `note`

---

## 粗利計算ルール（内部）
- `gross_margin_rate = (sales_unit_price - unit_cost_basis) / unit_cost_basis`
- split仕入れ時の `unit_cost_basis` は加重平均:
  - `Σ(purchased_qty_i × final_unit_cost_i) / Σ(purchased_qty_i)`
- `gross_margin_rate` は内部項目であり、請求書PDFには出力しない

## 3.3 請求書PDF（顧客向け）
Header fields:
- `invoice_no`
- `invoice_date`
- `delivery_date`
- `customer_name`
- `currency`（HKD）

Line fields:
- `description`
- `qty_display`
- `uom_display`
- `weight_kg`（catch-weight時）
- `unit_price`
- `amount`
- `tax_amount`

Totals:
- `subtotal`
- `tax_total`
- `grand_total`

Not printed on PDF:
- `gross_margin_rate`（内部項目のため非表示）

---

## 4) バリデーションI/O（エラー設計）

標準エラー形式:
- `code` (string)
- `message` (string)
- `field` (string, optional)
- `detail` (object/string, optional)

主なHTTP:
- `401` 認証不足
- `403` 権限不足
- `409` ステータス競合/遷移不可
- `422` 入力値不正

---

## 5) 確定事項（2026-03-11 FIX）
- `delivery_date` はAPI必須項目（Defaultは注文日の翌日、手動変更可）
- `target_price` は通常は任意。ただし `override_reason_code=better_price` または `urgent_delivery` の場合は必須
- supplier は自分の担当行に限り `final_unit_cost` を更新可（監査ログ必須）。ただし請求確定前に buyer/admin が最終確認を行う
