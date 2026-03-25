import React from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts'

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-bg-card border border-neon/30 rounded-lg px-3 py-2 shadow-neon">
      <p className="text-xs text-muted font-mono">Iter {label}</p>
      <p className="text-sm text-neon font-mono font-semibold">
        {payload[0].value.toFixed(2)}%
      </p>
    </div>
  )
}

export default function ResultsSection({ status }) {
  const convData = (status?.convergence ?? []).map((v, i) => ({
    iter: i + 1,
    accuracy: parseFloat((v * 100).toFixed(2)),
  }))

  const best = status?.best_accuracy ?? 0

  return (
    <div className="space-y-6 animate-fadein">
      {/* Metric cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Best Accuracy', value: `${(best * 100).toFixed(2)}%`, accent: 'text-neon', glow: 'shadow-neon' },
          { label: 'Total Time',    value: `${status.elapsed_seconds}s`,   accent: 'text-purple', glow: 'shadow-purple' },
          { label: 'Evaluations',   value: status.all_accuracies?.length ?? 0, accent: 'text-text' },
          { label: 'Iterations',    value: status.total_iterations,         accent: 'text-text' },
        ].map(({ label, value, accent, glow }) => (
          <div key={label} className={`glass-card p-5 flex flex-col gap-1 ${glow ?? ''}`}>
            <p className="text-xs text-muted font-mono uppercase tracking-wider">{label}</p>
            <p className={`font-display text-2xl font-bold ${accent}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Recharts convergence */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-5">
          <h3 className="font-display text-xs font-semibold text-neon uppercase tracking-widest">
            Convergence Curve
          </h3>
          <span className="text-xs font-mono text-muted/60">HGWO-PSO · {convData.length} iterations</span>
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={convData} margin={{ top: 5, right: 10, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
            <XAxis
              dataKey="iter"
              stroke="#4B5563"
              tick={{ fontSize: 10, fontFamily: 'JetBrains Mono', fill: '#6B7280' }}
              label={{ value: 'Iteration', position: 'insideBottom', offset: -2, fill: '#6B7280', fontSize: 10 }}
            />
            <YAxis
              stroke="#4B5563"
              tick={{ fontSize: 10, fontFamily: 'JetBrains Mono', fill: '#6B7280' }}
              domain={[0, 100]}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine
              y={best * 100}
              stroke="#7C3AED"
              strokeDasharray="4 4"
              strokeOpacity={0.6}
            />
            <Line
              type="monotone"
              dataKey="accuracy"
              stroke="#00E5FF"
              strokeWidth={2.5}
              dot={{ fill: '#7C3AED', r: 4, strokeWidth: 0 }}
              activeDot={{ r: 6, fill: '#00E5FF', strokeWidth: 2, stroke: '#0B0F14' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Server-rendered matplotlib figures */}
      {status.figures?.convergence && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="glass-card p-4">
            <p className="text-xs font-mono text-muted uppercase tracking-wider mb-3">
              Matplotlib · Convergence
            </p>
            <img
              src={status.figures.convergence}
              alt="convergence"
              className="w-full rounded-lg"
            />
          </div>
          <div className="glass-card p-4">
            <p className="text-xs font-mono text-muted uppercase tracking-wider mb-3">
              Matplotlib · Accuracy Distribution
            </p>
            <img
              src={status.figures.boxplot}
              alt="boxplot"
              className="w-full rounded-lg"
            />
          </div>
        </div>
      )}

      {/* Best hyperparameters note */}
      <div className="glass-card p-5">
        <p className="text-xs font-mono text-muted uppercase tracking-wider mb-3">Optimization Complete</p>
        <p className="text-sm text-text/80 font-body">
          HGWO-PSO converged after <span className="text-neon font-mono">{status.total_iterations}</span> iterations
          across <span className="text-neon font-mono">{status.all_accuracies?.length}</span> candidate evaluations.
          Best validation accuracy achieved:{' '}
          <span className="text-neon font-mono font-semibold">{(best * 100).toFixed(2)}%</span> on CIFAR-10 subset.
        </p>
      </div>
    </div>
  )
}
