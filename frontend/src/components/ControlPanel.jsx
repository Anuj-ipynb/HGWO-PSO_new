import React from 'react'

const FIELDS = [
  {
    key: 'epochs',
    label: 'Training Epochs',
    hint: 'per candidate',
    min: 1,
    max: 5,
    tip: 'Higher = more accurate but slower',
  },
  {
    key: 'population',
    label: 'Population Size',
    hint: 'wolves / particles',
    min: 4,
    max: 20,
    tip: 'Pack size for GWO + PSO swarm',
  },
  {
    key: 'iterations',
    label: 'Iterations',
    hint: 'optimization steps',
    min: 3,
    max: 30,
    tip: 'More iterations = better convergence',
  },
]

function NumberField({ field, value, onChange }) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <label className="text-xs font-mono text-muted uppercase tracking-wider">
          {field.label}
          <span className="ml-2 text-neon/50 normal-case">{field.hint}</span>
        </label>
        <span className="text-xs text-muted/60 font-mono">{field.min}–{field.max}</span>
      </div>
      <input
        type="number"
        min={field.min}
        max={field.max}
        value={value}
        onChange={(e) => onChange(Math.min(field.max, Math.max(field.min, +e.target.value)))}
        className="w-full bg-bg-dark border border-neon/20 rounded-lg px-3 py-2.5
          text-text font-mono text-sm focus:outline-none focus:border-neon/60
          focus:shadow-neon transition-all duration-200"
      />
      <p className="text-xs text-muted/50 font-body">{field.tip}</p>
    </div>
  )
}

export default function ControlPanel({ config, setConfig, onStart, loading }) {
  const update = (key) => (val) => setConfig((c) => ({ ...c, [key]: val }))

  const totalEvals = config.population * config.iterations
  const estSeconds = Math.round(totalEvals * config.epochs * 4)

  return (
    <div className="glass-card p-6 space-y-5 animate-fadein">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-xs font-semibold text-neon uppercase tracking-widest">
          Control Panel
        </h3>
        <span className="text-xs font-mono text-muted/60">
          ~{totalEvals} evals · ~{estSeconds}s
        </span>
      </div>

      {FIELDS.map((f) => (
        <NumberField key={f.key} field={f} value={config[f.key]} onChange={update(f.key)} />
      ))}

      {/* Hyperparameter tags */}
      <div>
        <p className="text-xs font-mono text-muted uppercase tracking-wider mb-2">Search Space (7D)</p>
        <div className="flex flex-wrap gap-1.5">
          {['lr', 'batch', 'dropout', 'f1', 'f2', 'f3', 'dense'].map((hp) => (
            <span
              key={hp}
              className="text-xs font-mono px-2 py-0.5 rounded border border-neon/20 text-neon/70 bg-neon/5"
            >
              {hp}
            </span>
          ))}
        </div>
      </div>

      <button
        onClick={onStart}
        disabled={loading}
        className="btn-glow w-full py-3.5 rounded-xl font-display font-bold text-sm
          text-bg-dark uppercase tracking-widest"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="inline-block w-4 h-4 border-2 border-bg-dark/30 border-t-bg-dark rounded-full animate-spin" />
            Optimizing…
          </span>
        ) : (
          '▶  Start Optimization'
        )}
      </button>
    </div>
  )
}
