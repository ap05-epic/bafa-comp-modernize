import { Routes, Route } from 'react-router-dom'

// The conversion loop adds one <Route> per converted screen below, e.g.:
//   import Login from './screens/Login'
//   <Route path="/login" element={<Login />} />
export default function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <div className="placeholder">
            <h1>new-ui</h1>
            <p>Converted screens appear here. The loop adds a route per screen.</p>
          </div>
        }
      />
    </Routes>
  )
}
