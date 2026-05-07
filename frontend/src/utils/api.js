const BASE_URL = "http://127.0.0.1:8000"

export const startOptimization = async (config) => {
  const res = await fetch(`${BASE_URL}/api/v1/optimize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(config),
  })
  return res.json()
}

export const fetchStatus = async (runId) => {
  const res = await fetch(`${BASE_URL}/api/v1/status/${runId}`)
  return res.json()
}
