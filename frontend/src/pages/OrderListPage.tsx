import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchOrders } from '../api/orders'
import type { Order } from '../types/order'
import { EmptyState, ErrorState, LoadingState } from '../components/ViewState'

export const OrderListPage = () => {
  const [orders, setOrders] = useState<Order[]>([])
  const [keyword, setKeyword] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchOrders(keyword)
      setOrders(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  return (
    <section>
      <h2>受注一覧</h2>
      <div className="toolbar">
        <input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="顧客名 / 受注番号（errorで失敗検証）"
        />
        <button onClick={() => void load()}>検索</button>
      </div>

      {loading ? <LoadingState /> : null}
      {!loading && error ? <ErrorState message={error} onRetry={() => void load()} /> : null}
      {!loading && !error && orders.length === 0 ? <EmptyState /> : null}

      {!loading && !error && orders.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>受注番号</th>
              <th>顧客</th>
              <th>金額</th>
              <th>状態</th>
              <th>日付</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>
                  <Link to={`/orders/${o.id}`}>{o.orderNo}</Link>
                </td>
                <td>{o.customerName}</td>
                <td>{o.amount.toLocaleString()}</td>
                <td>{o.status}</td>
                <td>{o.orderDate}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </section>
  )
}
