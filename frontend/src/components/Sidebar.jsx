import React from 'react'

const NAV_ITEMS = [
  { label: 'Dashboard', icon: '⬡', active: true },
  { label: 'Run History', icon: '◈', active: false },
  { label: 'Settings', icon: '◎', active: false },
]

export default function Sidebar() {
  return (
    <aside className="w-60 bg-bg-card border-r border-neon/10 flex flex-col shrink-0">
      {/* Logo */}
      <div className="p-6 border-b border-neon/10">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-neon to-purple flex items-center justify-center text-bg-dark font-display font-black text-sm">
            H
          </div>
          <div>
            <p className="font-display text-xs text-neon tracking-widest uppercase leading-none">CUDA</p>
            <p className="font-display text-xs text-muted tracking-wider uppercase leading-none mt-0.5">Engine</p>
          </div>
        </div>
        <h1 className="font-display text-base font-bold text-text leading-tight">
          HGWO-PSO
        </h1>
        <p className="text-xs text-muted font-body mt-0.5">Hyperparameter Optimizer</p>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-4 space-y-1">
        {NAV_ITEMS.map((item) => (
          <div
            key={item.label}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-body cursor-pointer transition-all duration-200 ${
              item.active
                ? 'bg-neon/10 text-neon border border-neon/20 shadow-neon/20'
                : 'text-muted hover:text-text hover:bg-white/5'
            }`}
          >
            <span className="text-base leading-none">{item.icon}</span>
            {item.label}
          </div>
        ))}
      </nav>

      {/* Algorithm info */}
      <div className="p-4 border-t border-neon/10 space-y-2">
        <p className="text-xs font-mono text-muted uppercase tracking-wider">Algorithm</p>
        <div className="space-y-1">
          {['Grey Wolf Optimizer', 'Particle Swarm', 'Hybrid Blend λ=0.5'].map((t) => (
            <div key={t} className="flex items-center gap-2">
              <div className="w-1 h-1 rounded-full bg-neon/60" />
              <p className="text-xs text-muted/80 font-mono">{t}</p>
            </div>
          ))}
        </div>
        <p className="text-xs text-muted/50 font-mono pt-1">v1.0.0 · GTX 1050 Ti</p>
      </div>
    </aside>
  )
}
