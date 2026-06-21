// Contract types -- mirror the original FA Comp Summary REST shapes (from recon).

export interface TokenResponse {
  apiAuthentication?: { accessToken?: string; tokenType?: string }
}

export interface ReportMetaItem {
  attributeCategory: string // TITLE | TABLE | LEGEND | FOOT
  attributeIdentifier: string
  attributeDefinition: string // JSON string, e.g. {"displayText":"..."} or {"tagValue":"A",...}
}
export interface ReportMetaResponse {
  effectivePeriod?: number
  reportIdentifier?: number
  reportMetaData?: ReportMetaItem[]
}

export interface ReportColumn {
  columnIndex: number
  columnSequence: number
  columnHeaderDescription: string
  columnVisibilityFlag: boolean
  columnActiveFlag?: boolean
  columnDefinition?: string
}
export interface ReportCustomizationResponse {
  reportCustomizationMetaData?: ReportColumn[]
}

export interface ReportRecord {
  data?: Array<{ columnIndex: number; columnValue: string | number }>
}
export interface ReportDataResponse {
  totalRowCount?: number
  records?: ReportRecord[]
}

// Compensation widget (rebuilt summary-shell box) -- see CONTRACT.md.
export interface CompRow {
  key: string // production | compNNA | clMtg
  label: string
  daily: string
  mtd: string
  ytd: string
}
export interface CompensationResponse {
  asOf?: string
  rows?: CompRow[]
}
