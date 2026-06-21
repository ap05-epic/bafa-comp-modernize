import { Routes, Route, Navigate } from 'react-router-dom'
import ManagerDashboard from './screens/ManagerDashboard'
import CompensationWidget from './screens/CompensationWidget'

// FA Comp Summary (BAFA Comp). Two screens:
//   /              -> the full-page FA Comp Summary dashboard (replaces business-analysis-next-ui)
//   /compensation  -> the rebuilt summary-shell Compensation widget
export default function App() {
  return (
    <Routes>
      <Route path="/" element={<ManagerDashboard />} />
      <Route path="/compensation" element={<CompensationWidget />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
