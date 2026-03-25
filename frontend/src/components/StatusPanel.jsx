import React from 'react'

const STATUS_STYLES = {
  queued:    'border-muted/30 text-muted bg-white/5',
  running:   'border-neon/50 text-neon bg-neon/10',
  completed: 'border-green-500/50 text-green-400 bg-green-500/10',
  error:     'border-red-500/50 text-red-400 bg-red-500/10',
  idle:      'border-muted/30 text-muted bg-white/5',
}

function MetricBox({ label, value, accent }) {
  return (
    <div className="bg-bg-dark rounded-lg p-3 border border-neon/10 space-y-1">
      <p className="text-xs text-muted font-mono uppercase tracking-wider">{label}</p>
      <p className={`text-sm font-mono font-semibold ${accent ?? 'text-text'}`}>{value}</p>
    </div>
  )
}

export default function StatusPanel({ runId, status, loading, error }) {
  const pct = status?.progress ?? 0
  const st  = status?.status ?? 'idle'

  return (
    <div className="glass-card p-6 space-y-5 animate-fadein">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-xs font-semibold text-neon uppercase tracking-widest">
          Live Status
        </h3>
        <span
          className={`px-2.5 py-1 rounded-full border text-xs font-mono ${STATUS_STYLES[st] ?? STATUS_STYLES.idle}`}
        >
          {st.toUpperCase()}
        </span>
      </div>

      {/* Run ID */}
      <div className="bg-bg-dark rounded-lg px-3 py-2 border border-neon/10 flex justify-between items-center">
        <span className="text-xs text-muted font-mono">Run ID</span>
        <span className="text-xs text-neon font-mono">{runId ?? '—'}</span>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-3 py-2">
          <p className="text-xs text-red-400 font-mono">{error}</p>
        </div>
      )}

      {/* Progress bar */}
      <div>
        <div className="flex justify-between text-xs font-mono text-muted mb-1.5">
          <span>Progress</span>
          <span>{pct}%</span>
        </div>
        <div className="h-2.5 bg-bg-dark rounded-full overflow-hidden border border-neon/10">
          <div
            className="h-full bg-gradient-to-r from-neon to-purple rounded-full transition-all duration-700 progress-glow"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-2 gap-3">
        <MetricBox
          label="Iteration"
          value={`${status?.iteration ?? 0} / ${status?.total_iterations ?? '—'}`}
        />
        <MetricBox
          label="Best Accuracy"
          value={status?.best_accuracy ? `${(status.best_accuracy * 100).toFixed(2)}%` : '—'}
          accent="text-neon"
        />
        <MetricBox
          label="Elapsed"
          value={status?.elapsed_seconds ? `${status.elapsed_seconds}s` : '—'}
        />
        <MetricBox
          label="Evaluations"
          value={status?.all_accuracies?.length ?? 0}
        />
      </div>

      {/* Live convergence mini-bar */}
      {status?.convergence?.length > 0 && (
        <div>
          <p className="text-xs text-muted font-mono uppercase tracking-wider mb-2">
            Convergence Trace
          </p>
          <div className="flex items-end gap-0.5 h-12">
            {status.convergence.map((v, i) => (
              <div
                key={i}
                className="flex-1 rounded-sm bg-gradient-to-t from-purple to-neon transition-all duration-300"
                style={{ height: `${Math.max(4, v * 100)}%`, opacity: 0.7 + (i / status.convergence.length) * 0.3 }}
              />
            ))}
          </div>
        </div>
      )}

      {/* Loading pulse */}
      {loading && st === 'running' && (
        <div className="flex items-center gap-2 text-xs text-neon/70 font-mono animate-pulse2">
          <span className="w-1.5 h-1.5 rounded-full bg-neon animate-ping" />
          GPU training candidate…
        </div>
      )}
    </div>
  )
}
