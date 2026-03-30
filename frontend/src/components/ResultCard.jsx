/**
 * ResultCard.jsx — Single parameter status card
 */
import React from 'react'

const STATUS_CONFIG = {
  Normal:   { bg: 'rgba(16,185,129,0.1)', border: '#10B981', badge: 'bg-emerald-500/20 text-emerald-400', dot: '#10B981' },
  Low:      { bg: 'rgba(245,158,11,0.1)', border: '#F59E0B', badge: 'bg-amber-500/20 text-amber-400',   dot: '#F59E0B' },
  High:     { bg: 'rgba(239,68,68,0.1)',  border: '#EF4444', badge: 'bg-red-500/20 text-red-400',       dot: '#EF4444' },
  Critical: { bg: 'rgba(185,28,28,0.15)', border: '#B91C1C', badge: 'bg-red-900/40 text-red-300',       dot: '#B91C1C' },
}

const PARAM_ICONS = {
  Hemoglobin:             '🩸',
  Glucose:                '🍬',
  Cholesterol:            '❤️',
  BloodPressureSystolic:  '💉',
  BloodPressureDiastolic: '💉',
  Platelets:              '🔬',
  WBC:                    '🦠',
  RBC:                    '💊',
  Creatinine:             '🫘',
  Urea:                   '⚗️',
}

function getBarPercent(value, rangeLow, rangeHigh, status) {
  // Map value onto a 0–100 scale where [rangeLow, rangeHigh] occupies 20%-80%
  const span = rangeHigh - rangeLow
  if (span === 0) return 50
  const ext = span * 1.5
  const min = rangeLow - ext
  const max = rangeHigh + ext
  return Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100))
}

export default function ResultCard({ name, data }) {
  const config = STATUS_CONFIG[data.status] || STATUS_CONFIG.Normal
  const barPct = getBarPercent(data.value, data.range_low, data.range_high, data.status)
  const displayName = name.replace('BloodPressure', 'BP ')

  return (
    <div
      className="rounded-2xl p-5 border animate-fade-in transition-transform hover:-translate-y-1 hover:shadow-xl hover:shadow-black/20"
      style={{ background: config.bg, borderColor: config.border }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-xl">{PARAM_ICONS[name] || '📋'}</span>
          <span className="font-semibold text-sm text-slate-200">{displayName}</span>
        </div>
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${config.badge}`}>
          {data.status}
        </span>
      </div>

      {/* Value */}
      <div className="mb-3">
        <span className="text-3xl font-bold" style={{ color: config.dot }}>
          {data.value}
        </span>
        <span className="text-slate-400 text-sm ml-1.5">{data.unit}</span>
      </div>

      {/* Range bar */}
      <div className="mb-2">
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-700"
            style={{
              width: `${barPct}%`,
              background: config.dot,
              boxShadow: `0 0 8px ${config.dot}60`,
            }}
          />
        </div>
      </div>

      <p className="text-xs text-slate-500">
        Normal: {data.range_low} – {data.range_high} {data.unit}
      </p>
    </div>
  )
}
