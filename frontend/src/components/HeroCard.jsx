import React from 'react'

export default function HeroCard({ status }) {
  const gpuActive = status?.status === 'running'
  const completed = status?.status === 'completed'

  return (
    <div className="glass-card scanlines relative p-6 flex items-center justify-between overflow-hidden">
      {/* Background glow blobs */}
      <div className="absolute -top-10 -left-10 w-48 h-48 bg-neon/5 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-10 -right-10 w-48 h-48 bg-purple/5 rounded-full blur-3xl pointer-events-none" />

      {/* Left: title */}
      <div className="relative z-10">
        <p className="text-xs font-mono text-neon tracking-widest uppercase mb-1">
          Neural Architecture Search
        </p>
        <h2 className="font-display text-2xl font-black text-text">
          CUDA Optimization Engine
        </h2>
        <p className="text-sm text-muted mt-1 font-body">
          Hybrid Grey Wolf · Particle Swarm · Deep CNN · 7-Dimensional Search Space
        </p>
      </div>

      {/* Right: GPU status badge */}
      <div className="relative z-10 flex flex-col items-end gap-3">
        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-full border text-xs font-mono transition-all duration-500 ${
            gpuActive
              ? 'border-neon/60 text-neon bg-neon/10 animate-glow'
              : completed
              ? 'border-green-500/50 text-green-400 bg-green-500/10'
              : 'border-muted/30 text-muted bg-white/5'
          }`}
        >
          <span
            className={`w-2 h-2 rounded-full ${
              gpuActive ? 'bg-neon animate-pulse' : completed ? 'bg-green-400' : 'bg-muted'
            }`}
          />
          GPU {gpuActive ? 'ACTIVE' : completed ? 'DONE' : 'IDLE'}
        </div>

        <div className="flex gap-2">
          {['CUDA', 'AMP', 'FP16'].map((tag) => (
            <span
              key={tag}
              className="text-xs font-mono px-2 py-0.5 rounded border border-purple/30 text-purple/80 bg-purple/5"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
