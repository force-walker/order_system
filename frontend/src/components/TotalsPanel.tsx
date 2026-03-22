export const TotalsPanel = ({
  subtotal,
  tax,
  total,
  marginAmount,
  marginRate,
  showMargin
}: {
  subtotal: number
  tax: number
  total: number
  marginAmount?: number
  marginRate?: number
  showMargin?: boolean
}) => (
  <div className="totals">
    <div><span>小計</span><strong>HKD {subtotal.toLocaleString()}</strong></div>
    <div><span>税額</span><strong>HKD {tax.toLocaleString()}</strong></div>
    <div><span>合計</span><strong>HKD {total.toLocaleString()}</strong></div>
    {showMargin ? (
      <>
        <div><span>粗利額（内部）</span><strong>HKD {(marginAmount ?? 0).toLocaleString()}</strong></div>
        <div><span>粗利率（内部）</span><strong>{(marginRate ?? 0).toFixed(2)}%</strong></div>
      </>
    ) : null}
  </div>
)
