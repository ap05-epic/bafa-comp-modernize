import { useEffect, useState } from 'react'
import { fetchReportMeta, fetchReportCustomization, fetchReport } from '../api/client'

// Full-page FA Comp Summary dashboard. Metadata-driven (title/columns/legend/footer come
// from the report metadata), three states: happy / no-data / backend-error.
type View = 'loading' | 'happy' | 'nodata' | 'error'

function qp(name: string, dflt: string): string {
  return new URLSearchParams(window.location.search).get(name) ?? dflt
}
function parseDef(s: string): Record<string, unknown> {
  try {
    return JSON.parse(s)
  } catch {
    return {}
  }
}

interface Legend {
  tagValue?: string
  displayText?: string
}

export default function ManagerDashboard() {
  const [view, setView] = useState<View>('loading')
  const [title, setTitle] = useState('')
  const [columns, setColumns] = useState<string[]>([])
  const [rows, setRows] = useState<string[][]>([])
  const [legends, setLegends] = useState<Legend[]>([])
  const [foots, setFoots] = useState<string[]>([])

  useEffect(() => {
    const id = qp('reportIdentifier', '100')
    const period = qp('effectivePeriod', '202504')
    const orgHierCode = qp('orgHierCode', '000')
    const orgHierRole = qp('orgHierRole', 'FA')
    const orgIdentifier = qp('orgIdentifier', qp('entityDisplayName', 'AB10'))

    void (async () => {
      try {
        const meta = await fetchReportMeta(id)
        const cust = await fetchReportCustomization(id)
        const md = meta.reportMetaData || []
        const titleDef = md
          .filter((m) => m.attributeCategory === 'TITLE')
          .map((m) => parseDef(m.attributeDefinition))[0] as { displayText?: string } | undefined
        setTitle(`${qp('entityDisplayName', '')} ${titleDef?.displayText || ''}`.trim())
        setLegends(
          md.filter((m) => m.attributeCategory === 'LEGEND').map((m) => parseDef(m.attributeDefinition) as Legend),
        )
        setFoots(
          md
            .filter((m) => m.attributeCategory === 'FOOT')
            .map((m) => (parseDef(m.attributeDefinition) as { displayText?: string }).displayText || '')
            .filter(Boolean),
        )
        setColumns(
          (cust.reportCustomizationMetaData || [])
            .filter((c) => c.columnVisibilityFlag)
            .map((c) => c.columnHeaderDescription),
        )

        let report
        try {
          report = await fetchReport(id, period, orgHierCode, orgHierRole, orgIdentifier)
        } catch {
          setView('error')
          return
        }
        const recs = report.records || []
        if (recs.length === 0) {
          setView('nodata')
          return
        }
        setRows(recs.map((r) => (r.data || []).map((d) => String(d.columnValue))))
        setView('happy')
      } catch {
        setView('error')
      }
    })()
  }, [])

  if (view === 'loading') {
    return <div className="loading">Loading FA Comp Summary...</div>
  }

  if (view === 'nodata') {
    return (
      <div className="manager-dashboard-container">
        <div className="error-message-text">There is no data for your selection.</div>
      </div>
    )
  }

  if (view === 'error') {
    return (
      <div className="manager-dashboard-container">
        <div className="error-message-text">
          There was a technical issue which prevented the launch of FA Comp Summary Dashboard. Please try again later or
          report this to the support team.
        </div>
      </div>
    )
  }

  return (
    <div className="manager-dashboard-container" data-testid="manager-dashboard">
      <div className="table-header-container">
        <div className="table-header">
          <h2>{title}</h2>
        </div>
      </div>
      <div className="table-container">
        <div className="grid-container">
          <div className="ag-theme-alpine">
            <div className="ag-header">
              {columns.map((c, i) => (
                <span className="ag-header-cell-text" key={i}>
                  {c}
                </span>
              ))}
            </div>
            <div className="ag-center-cols-container">
              {rows.map((r, i) => (
                <div className="ag-row" key={i}>
                  {r.map((v, j) => (
                    <span className="ag-cell" key={j}>
                      {v}
                    </span>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
      <div className="footer-container">
        <div className="left-group">
          {legends.map((l, i) => (
            <span className="tag-wrapper" key={i}>
              <span className="tag-text">{l.tagValue}</span> {l.displayText}
            </span>
          ))}
        </div>
        {foots.map((f, i) => (
          <div className="disclaimer-container" key={i}>
            <span className="disclaimer-text">{f}</span>
          </div>
        ))}
        <button className="export-button" type="button">
          Export to Excel
        </button>
      </div>
    </div>
  )
}
