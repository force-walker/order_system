import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchInvoiceById, transitionInvoiceStatus } from '../api/orders'
import type { Invoice } from '../types/order'
import { ErrorState, LoadingState } from '../components/ViewState'
import { StatusBadge } from '../components/StatusBadge'
import { OrderLinesTable } from '../components/OrderLinesTable'
import { calcTotals } from '../api/calc'
import { TotalsPanel } from '../components/TotalsPanel'

export const InvoiceDetailPage = () => {
  const { id = '' } = useParams()
  const [invoice, setInvoice] = useState<Invoice | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      setInvoice(await fetchInvoiceById(id))
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
  if (!invoice) return null

  const totals = calcTotals(invoice.lines)
  const nextStatus: Record<string, Invoice['status']> = {
    draft: 'finalized',
    finalized: 'sent'
  }

  const move = async () => {
    const next = nextStatus[invoice.status]
    if (!next) return
    await transitionInvoiceStatus(invoice.id, next)
    void load()
  }

  return (
    <section>
      <div className="head-row">
        <div>
          <h2>{invoice.invoiceNo}</h2>
          <p>{invoice.customerName}</p>
        </div>
        <StatusBadge value={invoice.status} />
      </div>

      <div className="meta-grid">
        <div>
          <strong>請求日</strong>
          <p>{invoice.invoiceDate}</p>
          <strong>支払期限</strong>
          <p>{invoice.dueDate}</p>
        </div>
        <div>
          <strong>請求先住所</strong>
          <p>{invoice.customerAddress ?? '-'}</p>
          <div className="actions">
            <button onClick={() => void move()}>次ステータスへ</button>
            <Link to={`/orders/${invoice.orderId}`}>受注へ戻る</Link>
          </div>
        </div>
      </div>

      <div className="tabs"><button className="active">Invoice Lines</button><button>Other Info</button></div>
      <OrderLinesTable lines={invoice.lines} />
      <TotalsPanel {...totals} showMargin />
    </section>
  )
}
