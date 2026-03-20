import { Link, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { fetchOrderById } from '../api/orders'
import type { Order } from '../types/order'
import { ErrorState, LoadingState } from '../components/ViewState'

export const OrderDetailPage = () => {
  const { id = '' } = useParams()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      setOrder(await fetchOrderById(id))
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

  return (
    <section>
      <h2>受注詳細</h2>
      <dl>
        <dt>受注番号</dt>
        <dd>{order.orderNo}</dd>
        <dt>顧客名</dt>
        <dd>{order.customerName}</dd>
        <dt>金額</dt>
        <dd>{order.amount.toLocaleString()}</dd>
        <dt>状態</dt>
        <dd>{order.status}</dd>
        <dt>受注日</dt>
        <dd>{order.orderDate}</dd>
        <dt>備考</dt>
        <dd>{order.note ?? '-'}</dd>
      </dl>
      <div className="actions">
        <Link to={`/orders/${order.id}/edit`}>編集</Link>
        <Link to="/orders">一覧へ戻る</Link>
      </div>
    </section>
  )
}
