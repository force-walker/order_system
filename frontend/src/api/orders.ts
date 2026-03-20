import { mockInvoices, mockOrders } from '../mocks/orders'
import type { Invoice, Order, SaveOrderInput } from '../types/order'

let ordersDb = [...mockOrders]
let invoiceDb = [...mockInvoices]

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export async function fetchOrders(keyword: string): Promise<Order[]> {
  await delay(280)
  if (keyword.toLowerCase() === 'error') throw new Error('一覧取得エラー（mock）')
  const q = keyword.trim().toLowerCase()
  if (!q) return ordersDb
  return ordersDb.filter(
    (o) => o.customerName.toLowerCase().includes(q) || o.orderNo.toLowerCase().includes(q)
  )
}

export async function fetchOrderById(id: string): Promise<Order> {
  await delay(220)
  const order = ordersDb.find((o) => o.id === id)
  if (!order) throw new Error('受注が見つかりません')
  return order
}

export async function saveOrder(input: SaveOrderInput): Promise<Order> {
  await delay(300)
  if (input.customerName.toLowerCase() === 'error') throw new Error('保存失敗（mock）')

  if (input.id) {
    const current = ordersDb.find((o) => o.id === input.id)
    if (!current) throw new Error('更新対象が見つかりません')
    const updated: Order = { ...current, ...input }
    ordersDb = ordersDb.map((o) => (o.id === updated.id ? updated : o))
    return updated
  }

  const created: Order = {
    id: String(Date.now()),
    orderNo: `SO${1600 + ordersDb.length + 1}`,
    ...input
  }
  ordersDb = [created, ...ordersDb]
  return created
}

export async function transitionOrderStatus(id: string, next: Order['status']) {
  await delay(180)
  ordersDb = ordersDb.map((o) => (o.id === id ? { ...o, status: next } : o))
}

export async function fetchInvoiceById(id: string): Promise<Invoice> {
  await delay(220)
  const invoice = invoiceDb.find((i) => i.id === id)
  if (!invoice) throw new Error('請求書が見つかりません')
  return invoice
}

export async function fetchInvoiceByOrderId(orderId: string): Promise<Invoice | null> {
  await delay(220)
  return invoiceDb.find((i) => i.orderId === orderId) ?? null
}

export async function transitionInvoiceStatus(id: string, next: Invoice['status']) {
  await delay(180)
  invoiceDb = invoiceDb.map((i) => (i.id === id ? { ...i, status: next } : i))
}
