import { Link } from 'react-router-dom'
import type { PropsWithChildren } from 'react'

export const AppLayout = ({ children }: PropsWithChildren) => (
  <div className="app-shell">
    <header className="topbar">
      <h1>受注管理UI（Mock）</h1>
      <nav>
        <Link to="/orders">受注一覧</Link>
        <Link to="/orders/new">新規作成</Link>
      </nav>
    </header>
    <main>{children}</main>
  </div>
)
