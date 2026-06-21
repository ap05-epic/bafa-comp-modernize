// Bundled sample data for VITE_MOCK=1 -- lets you boot the app and see it render WITHOUT
// any backend. Not used in real fetch mode (default) or by the verify kit (which stubs
// the network so it exercises the real fetch path).
import type {
  ReportMetaResponse,
  ReportCustomizationResponse,
  ReportDataResponse,
  CompensationResponse,
} from './types'

export const mockReportMeta: ReportMetaResponse = {
  effectivePeriod: 202504,
  reportIdentifier: 100,
  reportMetaData: [
    { attributeCategory: 'TITLE', attributeIdentifier: '1', attributeDefinition: '{"displayText":" FA Comp Summary Dashboard"}' },
    { attributeCategory: 'TABLE', attributeIdentifier: '2', attributeDefinition: '{"rowsPerPage":"50"}' },
    { attributeCategory: 'LEGEND', attributeIdentifier: '3', attributeDefinition: '{"tagValue":"A","displayText":"Above target"}' },
    { attributeCategory: 'FOOT', attributeIdentifier: '4', attributeDefinition: '{"displayText":"Demonstrative purposes only."}' },
  ],
}

export const mockReportCustomization: ReportCustomizationResponse = {
  reportCustomizationMetaData: [
    { columnIndex: 1, columnSequence: 1, columnHeaderDescription: 'FA ID', columnVisibilityFlag: true },
    { columnIndex: 2, columnSequence: 2, columnHeaderDescription: 'Name', columnVisibilityFlag: true },
  ],
}

export const mockReportData: ReportDataResponse = {
  totalRowCount: 2,
  records: [
    { data: [{ columnIndex: 1, columnValue: 'AB10' }, { columnIndex: 2, columnValue: 'Sample Name' }] },
    { data: [{ columnIndex: 1, columnValue: 'CD20' }, { columnIndex: 2, columnValue: 'Another Name' }] },
  ],
}

export const mockCompensation: CompensationResponse = {
  asOf: 'Apr 2026',
  rows: [
    { key: 'production', label: 'Production', daily: '12,500', mtd: '146,200', ytd: '1,284,900' },
    { key: 'compNNA', label: 'Comp NNA', daily: '3,100', mtd: '41,800', ytd: '402,650' },
    { key: 'clMtg', label: 'CL/MTG', daily: '880', mtd: '9,450', ytd: '88,120' },
  ],
}
