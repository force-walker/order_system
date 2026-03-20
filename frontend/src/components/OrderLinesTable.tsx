import type { OrderLine } from '../types/order'
import { calcLineAfterDiscount } from '../api/calc'

export const OrderLinesTable = ({ lines }: { lines: OrderLine[] }) => (
  <table>
    <thead>
      <tr>
        <th>商品</th>
        <th>数量</th>
        <th>UoM</th>
        <th>単価(HKD)</th>
        <th>値引%</th>
        <th>税率%</th>
        <th>金額(HKD)</th>
      </tr>
    </thead>
    <tbody>
      {lines.map((l) => (
        <tr key={l.id}>
          <td>{l.product}</td>
          <td>{l.qty}</td>
          <td>{l.uom}</td>
          <td>{l.unitPrice.toLocaleString()}</td>
          <td>{(l.discountRate * 100).toFixed(1)}</td>
          <td>{(l.taxRate * 100).toFixed(1)}</td>
          <td>{calcLineAfterDiscount(l).toLocaleString()}</td>
        </tr>
      ))}
    </tbody>
  </table>
)
