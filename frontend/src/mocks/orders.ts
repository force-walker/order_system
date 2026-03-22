import type { Invoice, Order } from '../types/order'

export const mockOrders: Order[] = [
  {
    id: '1',
    orderNo: 'SO1606',
    customerName: 'Simply Fresh Food Company Limited',
    customerAddress: 'Unit 12B, 12/F Wah Shing Centre, 5 Fung Yip St, Chai Wan, Hong Kong',
    status: 'confirmed',
    orderDate: '2026-03-18',
    note: '優先対応',
    lines: [
      { id: 'l1', product: 'Farmed Bluefin Tuna F-size belly approx. 8kg/CS', qty: 16, uom: 'Units', unitPrice: 324, taxRate: 0.08, discountRate: 0, unitCost: 245 },
      { id: 'l2', product: 'Farmed Bluefin Tuna L-size Akami approx. 20kg/CS', qty: 20, uom: 'Units', unitPrice: 196, taxRate: 0.08, discountRate: 0, unitCost: 151 },
      { id: 'l3', product: 'Farmed Southern Bluefin Tuna Akami approx. 20kg/CS', qty: 30, uom: 'Units', unitPrice: 145, taxRate: 0.08, discountRate: 0, unitCost: 115 }
    ]
  },
  {
    id: '2',
    orderNo: 'SO1607',
    customerName: 'Koji Trading',
    status: 'new',
    orderDate: '2026-03-19',
    lines: [
      { id: 'l1', product: 'Frozen Oyster Bulk 80-89g', qty: 100, uom: 'kg', unitPrice: 70, taxRate: 0.08, discountRate: 0.02, unitCost: 58 }
    ]
  }
]

export const mockInvoices: Invoice[] = [
  {
    id: 'inv-1',
    invoiceNo: 'INV/2025/00014',
    orderId: '1',
    customerName: 'Simply Fresh Food Company Limited',
    customerAddress: 'Unit 12B, 12/F Wah Shing Centre, 5 Fung Yip St, Chai Wan, Hong Kong',
    invoiceDate: '2026-03-20',
    dueDate: '2026-03-31',
    status: 'draft',
    lines: [
      { id: 'il1', product: 'Farmed Bluefin Tuna F-size belly approx. 8kg/CS', qty: 16, uom: 'Units', unitPrice: 324, taxRate: 0.08, discountRate: 0, unitCost: 245 },
      { id: 'il2', product: 'Farmed Bluefin Tuna L-size Akami approx. 20kg/CS', qty: 20, uom: 'Units', unitPrice: 196, taxRate: 0.08, discountRate: 0, unitCost: 151 }
    ]
  }
]
