import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { fetchOrderById, saveOrder } from '../api/orders'
import { ErrorState, LoadingState, SuccessBanner } from '../components/ViewState'
import type { OrderStatus } from '../types/order'

const statuses: OrderStatus[] = ['Draft', 'Confirmed', 'Shipped']

type Props = { mode: 'create' | 'edit' }

export const OrderFormPage = ({ mode }: Props) => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(mode === 'edit')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [form, setForm] = useState({
    customerName: '',
    amount: 0,
    status: 'Draft' as OrderStatus,
    orderDate: new Date().toISOString().slice(0, 10),
    note: ''
  })

  useEffect(() => {
    if (mode !== 'edit' || !id) return
    const load = async () => {
      try {
        const o = await fetchOrderById(id)
        setForm({
          customerName: o.customerName,
          amount: o.amount,
          status: o.status,
          orderDate: o.orderDate,
          note: o.note ?? ''
        })
      } catch (e) {
        setError((e as Error).message)
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [mode, id])

  const validationErrors = {
    customerName: form.customerName.trim() ? '' : '顧客名は必須です',
    amount: form.amount > 0 ? '' : '金額は0より大きい値を入力してください'
  }
  const hasError = Object.values(validationErrors).some(Boolean)

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    if (hasError) return
    setSaving(true)
    try {
      const saved = await saveOrder({ id: mode === 'edit' ? id : undefined, ...form })
      setSuccess(`保存成功: ${saved.orderNo}`)
      setTimeout(() => navigate('/orders'), 600)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <LoadingState />

  return (
    <section>
      <h2>{mode === 'create' ? '受注新規作成' : '受注編集'}</h2>
      {success ? <SuccessBanner>{success}</SuccessBanner> : null}
      {error ? <ErrorState message={error} /> : null}
      <form onSubmit={onSubmit} className="form">
        <label>
          顧客名（必須）
          <input
            value={form.customerName}
            onChange={(e) => setForm({ ...form, customerName: e.target.value })}
          />
          {validationErrors.customerName ? <small>{validationErrors.customerName}</small> : null}
        </label>

        <label>
          金額（必須）
          <input
            type="number"
            value={form.amount}
            onChange={(e) => setForm({ ...form, amount: Number(e.target.value) })}
          />
          {validationErrors.amount ? <small>{validationErrors.amount}</small> : null}
        </label>

        <label>
          状態
          <select
            value={form.status}
            onChange={(e) => setForm({ ...form, status: e.target.value as OrderStatus })}
          >
            {statuses.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        <label>
          受注日
          <input
            type="date"
            value={form.orderDate}
            onChange={(e) => setForm({ ...form, orderDate: e.target.value })}
          />
        </label>

        <label>
          備考
          <textarea value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} />
        </label>

        <div className="actions">
          <button type="submit" disabled={saving || hasError}>
            {saving ? '保存中...' : '保存'}
          </button>
          <Link to="/orders">キャンセル</Link>
        </div>
      </form>
    </section>
  )
}
