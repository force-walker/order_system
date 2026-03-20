import { mockOrders } from '../mocks/orders'
import type { Order, SaveOrderInput } from '../types/order'

let db = [...mockOrders]

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

export async function fetchOrders(keyword: string): Promise<Order[]> {
  await delay(350)
  if (keyword.toLowerCase() === 'error') {
    throw new Error('一覧取得エラー（mock）')
  }
  const q = keyword.trim().toLowerCase()
  if (!q) return db
  return db.filter(
    (o) => o.customerName.toLowerCase().includes(q) || o.orderNo.toLowerCase().includes(q)
  )
}

export async function fetchOrderById(id: string): Promise<Order> {
  await delay(300)
  const order = db.find((o) => o.id === id)
  if (!order) throw new Error('受注が見つかりません')
  return order
}

export async function saveOrder(input: SaveOrderInput): Promise<Order> {
  await delay(400)
  if (input.customerName.toLowerCase() === 'error') {
    throw new Error('保存失敗（mock）')
  }

  if (input.id) {
    const current = db.find((o) => o.id === input.id)
    if (!current) throw new Error('更新対象が見つかりません')
    const updated: Order = { ...current, ...input }
    db = db.map((o) => (o.id === updated.id ? updated : o))
    return updated
  }

  const created: Order = {
    id: String(Date.now()),
    orderNo: `ORD-${new Date().toISOString().slice(0, 10).replace(/-/g, '')}-${db.length + 1}`,
    ...input
  }
  db = [created, ...db]
  return created
}
