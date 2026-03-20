import type { Order } from '../types/order'

export const mockOrders: Order[] = [
  {
    id: '1',
    orderNo: 'ORD-20260320-001',
    customerName: 'Koji Trading',
    amount: 128000,
    status: 'Confirmed',
    orderDate: '2026-03-20',
    note: '優先対応'
  },
  {
    id: '2',
    orderNo: 'ORD-20260320-002',
    customerName: 'Northwind HK',
    amount: 76000,
    status: 'Draft',
    orderDate: '2026-03-19'
  },
  {
    id: '3',
    orderNo: 'ORD-20260320-003',
    customerName: 'Blue Ocean Ltd.',
    amount: 219000,
    status: 'Shipped',
    orderDate: '2026-03-18'
  }
]
