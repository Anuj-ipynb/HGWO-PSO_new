const BASE = '/api/v1'

export async function startOptimization(params) {
  const res = await fetch(`${BASE}/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) throw new Error(`Server error ${res.status}`)
  return res.json()
}

export async function fetchStatus(runId) {
  const res = await fetch(`${BASE}/status/${runId}`)
  if (!res.ok) throw new Error(`Status error ${res.status}`)
  return res.json()
}
