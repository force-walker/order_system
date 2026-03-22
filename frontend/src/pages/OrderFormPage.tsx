import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { fetchOrderById, saveOrder } from '../api/orders'
import { ErrorState, LoadingState, SuccessBanner } from '../components/ViewState'
import type { OrderLine, OrderStatus } from '../types/order'

const statuses: OrderStatus[] = ['new', 'confirmed', 'allocated', 'purchased', 'shipped', 'invoiced', 'cancelled']

type Props = { mode: 'create' | 'edit' }

const newLine = (): OrderLine => ({
  id: String(Date.now()),
  product: '',
  qty: 1,
  uom: 'Units',
  unitPrice: 0,
  taxRate: 0.08,
  discountRate: 0,
  unitCost: 0
})

export const OrderFormPage = ({ mode }: Props) => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(mode === 'edit')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [form, setForm] = useState({
    customerName: '',
    customerAddress: '',
    status: 'new' as OrderStatus,
    orderDate: new Date().toISOString().slice(0, 10),
    note: '',
    lines: [newLine()]
  })

  useEffect(() => {
    if (mode !== 'edit' || !id) return
    const load = async () => {
      try {
        const o = await fetchOrderById(id)
        setForm({
          customerName: o.customerName,
          customerAddress: o.customerAddress ?? '',
          status: o.status,
          orderDate: o.orderDate,
          note: o.note ?? '',
          lines: o.lines
        })
      } catch (e) {
        setError((e as Error).message)
      } finally {
        setLoading(false)
      }
    }
    void load()
  }, [mode, id])

  const validationError = !form.customerName.trim() || form.lines.some((l) => !l.product || l.qty <= 0 || l.unitPrice < 0)

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (validationError) return
    setSaving(true)
    try {
      const saved = await saveOrder({ id: mode === 'edit' ? id : undefined, ...form })
      setSuccess(`保存成功: ${saved.orderNo}`)
      setTimeout(() => navigate('/orders'), 500)
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
        <label>顧客名（必須）<input value={form.customerName} onChange={(e) => setForm({ ...form, customerName: e.target.value })} /></label>
        <label>顧客住所<input value={form.customerAddress} onChange={(e) => setForm({ ...form, customerAddress: e.target.value })} /></label>
        <label>状態<select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value as OrderStatus })}>{statuses.map((s) => <option key={s} value={s}>{s}</option>)}</select></label>
        <label>受注日<input type="date" value={form.orderDate} onChange={(e) => setForm({ ...form, orderDate: e.target.value })} /></label>
        <label>備考<textarea value={form.note} onChange={(e) => setForm({ ...form, note: e.target.value })} /></label>

        <h3>明細</h3>
        {form.lines.map((line, idx) => (
          <div key={line.id} className="line-edit">
            <input placeholder="商品" value={line.product} onChange={(e) => {
              const lines = [...form.lines]; lines[idx] = { ...line, product: e.target.value }; setForm({ ...form, lines })
            }} />
            <input type="number" placeholder="数量" value={line.qty} onChange={(e) => { const lines = [...form.lines]; lines[idx] = { ...line, qty: Number(e.target.value) }; setForm({ ...form, lines }) }} />
            <input placeholder="UoM" value={line.uom} onChange={(e) => { const lines = [...form.lines]; lines[idx] = { ...line, uom: e.target.value }; setForm({ ...form, lines }) }} />
            <input type="number" placeholder="単価" value={line.unitPrice} onChange={(e) => { const lines = [...form.lines]; lines[idx] = { ...line, unitPrice: Number(e.target.value) }; setForm({ ...form, lines }) }} />
            <button type="button" onClick={() => setForm({ ...form, lines: form.lines.filter((_, i) => i !== idx) })}>削除</button>
          </div>
        ))}
        <button type="button" onClick={() => setForm({ ...form, lines: [...form.lines, newLine()] })}>行追加</button>

        {validationError ? <small>顧客名と明細（商品/数量/単価）を確認してください</small> : null}
        <div className="actions">
          <button type="submit" disabled={saving || validationError}>{saving ? '保存中...' : '保存'}</button>
          <Link to="/orders">キャンセル</Link>
        </div>
      </form>
    </section>
  )
}
