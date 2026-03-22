export type OrderStatus = 'new' | 'confirmed' | 'allocated' | 'purchased' | 'shipped' | 'invoiced' | 'cancelled'
export type InvoiceStatus = 'draft' | 'finalized' | 'sent' | 'cancelled'

export type OrderLine = {
  id: string
  product: string
  qty: number
  uom: string
  unitPrice: number
  taxRate: number
  discountRate: number
  unitCost?: number
}

export type Order = {
  id: string
  orderNo: string
  customerName: string
  customerAddress?: string
  status: OrderStatus
  orderDate: string
  note?: string
  lines: OrderLine[]
}

export type SaveOrderInput = {
  id?: string
  customerName: string
  customerAddress?: string
  status: OrderStatus
  orderDate: string
  note?: string
  lines: OrderLine[]
}

export type Invoice = {
  id: string
  invoiceNo: string
  orderId: string
  customerName: string
  customerAddress?: string
  invoiceDate: string
  dueDate: string
  status: InvoiceStatus
  lines: OrderLine[]
}
