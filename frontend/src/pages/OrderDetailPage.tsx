import { Link, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { fetchInvoiceByOrderId, fetchOrderById, transitionOrderStatus } from '../api/orders'
import type { Invoice, Order } from '../types/order'
import { ErrorState, LoadingState } from '../components/ViewState'
import { StatusBadge } from '../components/StatusBadge'
import { OrderLinesTable } from '../components/OrderLinesTable'
import { TotalsPanel } from '../components/TotalsPanel'
import { calcTotals } from '../api/calc'
import { ChatterPanel } from '../components/ChatterPanel'

export const OrderDetailPage = () => {
  const { id = '' } = useParams()
  const [order, setOrder] = useState<Order | null>(null)
  const [invoice, setInvoice] = useState<Invoice | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const o = await fetchOrderById(id)
      setOrder(o)
      setInvoice(await fetchInvoiceByOrderId(o.id))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [id])

  if (loading) return <LoadingState />
  if (error) return <ErrorState message={error} onRetry={() => void load()} />
  if (!order) return null

  const totals = calcTotals(order.lines)

  const quickTransition = async () => {
    const map: Record<string, Order['status']> = {
      new: 'confirmed',
      confirmed: 'shipped',
      shipped: 'invoiced'
    }
    const next = map[order.status]
    if (!next) return
    await transitionOrderStatus(order.id, next)
    void load()
  }

  return (
    <section>
      <div className="head-row">
        <div>
          <h2>{order.orderNo}</h2>
          <p>{order.customerName}</p>
        </div>
        <StatusBadge value={order.status} />
      </div>

      <div className="meta-grid">
        <div>
          <strong>注文日</strong>
          <p>{order.orderDate}</p>
          <strong>顧客住所</strong>
          <p>{order.customerAddress ?? '-'}</p>
        </div>
        <div>
          <strong>メモ</strong>
          <p>{order.note ?? '-'}</p>
          <div className="actions">
            <button onClick={() => void quickTransition()}>次ステータスへ</button>
            <Link to={`/orders/${order.id}/edit`}>編集</Link>
            {invoice ? <Link to={`/invoices/${invoice.id}`}>請求書を見る</Link> : null}
          </div>
        </div>
      </div>

      <OrderLinesTable lines={order.lines} />
      <TotalsPanel {...totals} />

      <div className="grid-2">
        <div />
        <ChatterPanel />
      </div>
    </section>
  )
}
