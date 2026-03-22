import type { OrderLine } from '../types/order'

export const floor2 = (n: number) => Math.floor(n * 100) / 100

export const calcLineSubtotal = (line: OrderLine) => line.qty * line.unitPrice
export const calcLineAfterDiscount = (line: OrderLine) => {
  const subtotal = calcLineSubtotal(line)
  return floor2(subtotal * (1 - line.discountRate))
}

export const calcTotals = (lines: OrderLine[]) => {
  const subtotal = floor2(lines.reduce((acc, l) => acc + calcLineAfterDiscount(l), 0))
  const avgTaxRate = lines.length ? lines.reduce((a, l) => a + l.taxRate, 0) / lines.length : 0
  const tax = floor2(subtotal * avgTaxRate)
  const total = floor2(subtotal + tax)
  const totalCost = floor2(lines.reduce((acc, l) => acc + (l.unitCost ?? 0) * l.qty, 0))
  const marginAmount = floor2(subtotal - totalCost)
  const marginRate = subtotal > 0 ? floor2((marginAmount / subtotal) * 100) : 0
  return { subtotal, tax, total, marginAmount, marginRate }
}
