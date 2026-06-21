// API client -- same flow as the original: GET /auth/token first, then bearer-auth the
// data calls. Bases are env-configurable so it connects to the real backend in the pod.
// VITE_MOCK=1 short-circuits to bundled sample data (no backend needed).
import type {
  ReportMetaResponse,
  ReportCustomizationResponse,
  ReportDataResponse,
  CompensationResponse,
} from './types'
import {
  mockReportMeta,
  mockReportCustomization,
  mockReportData,
  mockCompensation,
} from './mockData'

const AUTH_BASE = import.meta.env.VITE_AUTH_BASE || '/BAA/api'
const DATA_BASE = import.meta.env.VITE_DATA_BASE || '/BAA/api'
const COMP_BASE = import.meta.env.VITE_COMP_BASE || '/BAA/api'
const MOCK = !!import.meta.env.VITE_MOCK

class HttpError extends Error {
  status: number
  constructor(status: number) {
    super(`HTTP ${status}`)
    this.status = status
  }
}

let token: string | null = null

async function getToken(): Promise<string> {
  if (MOCK) return 'mock-token'
  if (token) return token
  const res = await fetch(`${AUTH_BASE}/auth/token`)
  if (!res.ok) throw new HttpError(res.status)
  const body = (await res.json()) as TokenResponseLike
  token = body?.apiAuthentication?.accessToken || ''
  return token
}
type TokenResponseLike = { apiAuthentication?: { accessToken?: string } }

async function jget<T>(url: string): Promise<T> {
  const t = await getToken()
  const res = await fetch(url, { headers: t ? { Authorization: `Bearer ${t}` } : {} })
  if (!res.ok) throw new HttpError(res.status)
  return (await res.json()) as T
}

export async function fetchReportMeta(id: string): Promise<ReportMetaResponse> {
  if (MOCK) return mockReportMeta
  return jget<ReportMetaResponse>(`${DATA_BASE}/report-meta-data/${id}`)
}

export async function fetchReportCustomization(id: string): Promise<ReportCustomizationResponse> {
  if (MOCK) return mockReportCustomization
  return jget<ReportCustomizationResponse>(`${DATA_BASE}/report-customization-metadata/${id}`)
}

export async function fetchReport(
  id: string,
  period: string,
  orgHierCode: string,
  orgHierRole: string,
  orgIdentifier: string,
): Promise<ReportDataResponse> {
  if (MOCK) return mockReportData
  return jget<ReportDataResponse>(`${DATA_BASE}/reports/${id}/${period}/${orgHierCode}/${orgHierRole}/${orgIdentifier}`)
}

export async function fetchCompensation(fa: string): Promise<CompensationResponse> {
  if (MOCK) return mockCompensation
  return jget<CompensationResponse>(`${COMP_BASE}/fa-compensation/${fa}`)
}
