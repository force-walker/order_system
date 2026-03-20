export type OrderStatus = 'Draft' | 'Confirmed' | 'Shipped'

export type Order = {
  id: string
  orderNo: string
  customerName: string
  amount: number
  status: OrderStatus
  orderDate: string
  note?: string
}

export type SaveOrderInput = {
  id?: string
  customerName: string
  amount: number
  status: OrderStatus
  orderDate: string
  note?: string
}
