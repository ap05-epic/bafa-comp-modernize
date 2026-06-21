import { useEffect, useState } from 'react'
import { fetchCompensation } from '../api/client'
import type { CompRow } from '../api/types'

// Rebuilt summary-shell Compensation widget. Exposes the data-testid CONTRACT so the
// verify kit asserts it. Three states: happy / no-data / backend-error.
type View = 'loading' | 'happy' | 'nodata' | 'error'

function qp(name: string, dflt: string): string {
  return new URLSearchParams(window.location.search).get(name) ?? dflt
}

export default function CompensationWidget() {
  const [view, setView] = useState<View>('loading')
  const [asOf, setAsOf] = useState('')
  const [rows, setRows] = useState<CompRow[]>([])

  useEffect(() => {
    const fa = qp('fa', 'AB10')
    void (async () => {
      try {
        const data = await fetchCompensation(fa)
        const rws = data.rows || []
        if (rws.length === 0) {
          setView('nodata')
          return
        }
        setAsOf(data.asOf || '')
        setRows(rws)
        setView('happy')
      } catch {
        setView('error')
      }
    })()
  }, [])

  if (view === 'loading') {
    return <div className="loading">Loading Compensation...</div>
  }

  if (view === 'nodata') {
    return (
      <div className="comp-widget" data-testid="comp-widget">
        <div className="comp-title" data-testid="comp-title">
          Compensation
        </div>
        <div className="comp-error" data-testid="comp-error">
          There is no compensation data for this selection.
        </div>
      </div>
    )
  }

  if (view === 'error') {
    return (
      <div className="comp-widget" data-testid="comp-widget">
        <div className="comp-title" data-testid="comp-title">
          Compensation
        </div>
        <div className="comp-error" data-testid="comp-error">
          Business Analysis Application Error
        </div>
      </div>
    )
  }

  const byKey = (k: string): Partial<CompRow> => rows.find((r) => r.key === k) || {}
  const row = (k: string, label: string) => {
    const r = byKey(k)
    const tid = k.toLowerCase()
    return (
      <tr className={`comp-row comp-row-${tid}`} data-testid={`comp-row-${tid}`}>
        <td className="comp-label">{label}</td>
        <td className="comp-cell num" data-testid={`comp-cell-${tid}-daily`}>
          {r.daily}
        </td>
        <td className="comp-cell num" data-testid={`comp-cell-${tid}-mtd`}>
          {r.mtd}
        </td>
        <td className="comp-cell num" data-testid={`comp-cell-${tid}-ytd`}>
          {r.ytd}
        </td>
      </tr>
    )
  }

  return (
    <div className="comp-widget" data-testid="comp-widget">
      <div className="comp-title" data-testid="comp-title">
        Compensation
      </div>
      <table className="cw3">
        <thead>
          <tr>
            <th>Schedule C</th>
            <th className="num">Daily</th>
            <th className="num">MTD</th>
            <th className="num">YTD</th>
          </tr>
        </thead>
        <tbody>
          {row('production', 'Production')}
          {row('compNNA', 'Comp NNA')}
          {row('clMtg', 'CL/MTG')}
        </tbody>
      </table>
      <div className="comp-asof" data-testid="comp-asof">
        {asOf}
      </div>
    </div>
  )
}
