const dummy = [
  'Quotation confirmed',
  'Sales Order created',
  'Invoice generated'
]

export const ChatterPanel = () => (
  <aside className="chatter">
    <h3>活動ログ（ダミー）</h3>
    <ul>
      {dummy.map((d, i) => (
        <li key={i}>{d}</li>
      ))}
    </ul>
  </aside>
)
