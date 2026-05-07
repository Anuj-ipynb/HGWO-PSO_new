import React, { useState, useEffect, useRef } from 'react'
import Sidebar from './components/Sidebar'
import HeroCard from './components/HeroCard'
import ControlPanel from './components/ControlPanel'
import StatusPanel from './components/StatusPanel'
import ResultsSection from './components/ResultsSection'
import { startOptimization, fetchStatus } from './utils/api'

export default function App() {
  // ✅ SAFE CONFIG FOR DEMO
  const [config, setConfig] = useState({ epochs: 5, population: 5, iterations: 7 })

  const [runId, setRunId] = useState(null)
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)


  const handleStart = async () => {
    setLoading(true)
    setError(null)
    setStatus(null)
    setRunId(null)
    try {
      const { run_id } = await startOptimization(config)
      setRunId(run_id)
    } catch (e) {
      setError(e.message)
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!runId) return

    const poll = async () => {
      try {
        const data = await fetchStatus(runId)
        setStatus(data)

        if (data.status === 'completed' || data.status === 'error') {
          clearInterval(pollRef.current)
          setLoading(false)
        }
      } catch (e) {
        clearInterval(pollRef.current)
        setError(e.message)
        setLoading(false)
      }
    }

    poll()
    pollRef.current = setInterval(poll, 2500)

    return () => clearInterval(pollRef.current)
  }, [runId])

  return (
    <div className="flex h-screen overflow-hidden bg-bg-dark grid-bg">
      <Sidebar />

      <main className="flex-1 overflow-y-auto p-6 space-y-6">

        {/* 🔥 HERO */}
        <HeroCard status={status} />

        {/* 🔥 RUNNING STATUS MESSAGE */}
        {loading && (
          <div className="text-yellow-400 font-semibold animate-pulse">
            🚀 Running HGWO-PSO Optimization...
          </div>
        )}

        {/* 🔴 ERROR */}
        {error && (
          <div className="text-red-500 font-semibold">
            ❌ Error: {error}
          </div>
        )}

        {/* 🔧 CONTROL + STATUS */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ControlPanel
            config={config}
            setConfig={setConfig}
            onStart={handleStart}
            loading={loading}
          />

          <StatusPanel runId={runId} status={status} loading={loading} error={error} />
        </div>

        {/* 📊 PROGRESS BAR */}
        {status?.progress !== undefined && (
          <div className="w-full bg-gray-700 rounded h-3">
            <div
              className="bg-green-500 h-3 rounded transition-all duration-500"
              style={{ width: `${status.progress}%` }}
            ></div>
          </div>
        )}

        {/* 📈 RESULTS */}
        {status?.status === 'completed' && (
          <ResultsSection status={status} />
        )}

      </main>
    </div>
  )
}