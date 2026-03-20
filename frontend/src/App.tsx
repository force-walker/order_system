import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './layouts/AppLayout'
import { OrderListPage } from './pages/OrderListPage'
import { OrderDetailPage } from './pages/OrderDetailPage'
import { OrderFormPage } from './pages/OrderFormPage'
import { InvoiceDetailPage } from './pages/InvoiceDetailPage'

export const App = () => (
  <AppLayout>
    <Routes>
      <Route path="/" element={<Navigate to="/orders" replace />} />
      <Route path="/orders" element={<OrderListPage />} />
      <Route path="/orders/new" element={<OrderFormPage mode="create" />} />
      <Route path="/orders/:id" element={<OrderDetailPage />} />
      <Route path="/orders/:id/edit" element={<OrderFormPage mode="edit" />} />
      <Route path="/invoices/:id" element={<InvoiceDetailPage />} />
    </Routes>
  </AppLayout>
)
