/**
 * Dashboard.jsx — Full analysis results dashboard
 */
import React, { useState } from 'react'
import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, Tooltip, ResponsiveContainer,
} from 'recharts'
import {
  Download, AlertTriangle, CheckCircle, Activity, FileText, RotateCcw,
} from 'lucide-react'
import ResultCard from './ResultCard'
import axios from 'axios'

const API = '/api'

const OVERALL_CONFIG = {
  'Healthy':            { color: '#10B981', icon: <CheckCircle className="w-6 h-6" />, label: 'Healthy' },
  'Needs Attention':    { color: '#F59E0B', icon: <AlertTriangle className="w-6 h-6" />, label: 'Needs Attention' },
  'Critical':           { color: '#EF4444', icon: <AlertTriangle className="w-6 h-6" />, label: 'Critical' },
  'Insufficient Data':  { color: '#94A3B8', icon: <Activity className="w-6 h-6" />, label: 'Insufficient Data' },
}

const SEVERITY_STYLE = {
  Critical: 'border-red-900/50 bg-red-900/20 text-red-300',
  High:     'border-red-500/40 bg-red-500/10 text-red-400',
  Moderate: 'border-amber-500/40 bg-amber-500/10 text-amber-400',
  Low:      'border-emerald-500/40 bg-emerald-500/10 text-emerald-400',
}

const TABS = ['Overview', 'Parameters', 'Risks', 'Raw Text']

function buildRadarData(parameters) {
  return Object.entries(parameters).map(([name, data]) => {
    const span = data.range_high - data.range_low || 1
    const norm = Math.min(100, Math.max(0, ((data.value - data.range_low) / span) * 100 + 50))
    return { subject: name.replace('BloodPressure', 'BP'), value: Math.round(norm), fullMark: 150 }
  })
}

export default function Dashboard({ result, onReset }) {
  const [tab, setTab] = useState('Overview')
  const [downloading, setDownloading] = useState(false)

  const { report_id, filename, upload_time, parameters = {}, risks = [], summary = {}, extracted_text } = result
  const overall = OVERALL_CONFIG[summary.overall_status] || OVERALL_CONFIG['Insufficient Data']
  const radarData = buildRadarData(parameters)
  const paramEntries = Object.entries(parameters)
  const abnormalParams = paramEntries.filter(([, d]) => d.status !== 'Normal')

  const handleDownload = async () => {
    setDownloading(true)
    try {
      const res = await axios.get(`${API}/download/${report_id}`, { responseType: 'blob' })
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const a = document.createElement('a')
      a.href = url
      a.download = `medscan_report_${report_id}.pdf`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      alert('PDF download failed. Please try again.')
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="w-full max-w-6xl mx-auto animate-fade-in">

      {/* Top bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center"
              style={{ background: `${overall.color}25`, color: overall.color }}
            >
              {overall.icon}
            </div>
            <div>
              <p className="text-xs text-slate-500 uppercase tracking-widest">Overall Status</p>
              <p className="text-xl font-bold" style={{ color: overall.color }}>
                {summary.overall_status}
              </p>
            </div>
          </div>
          <p className="text-sm text-slate-500 mt-2">
            <FileText className="inline w-3.5 h-3.5 mr-1 -mt-0.5" />
            {filename}  ·  {new Date(upload_time).toLocaleString()}
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleDownload}
            disabled={downloading}
            className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-xl font-medium text-sm transition-all shadow-lg shadow-blue-500/20"
          >
            <Download className="w-4 h-4" />
            {downloading ? 'Generating…' : 'Download PDF'}
          </button>
          <button
            onClick={onReset}
            className="flex items-center gap-2 px-5 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-xl font-medium text-sm transition-all"
          >
            <RotateCcw className="w-4 h-4" />
            New Report
          </button>
        </div>
      </div>

      {/* Stat strip */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {[
          { label: 'Parameters Detected', value: summary.total_detected, color: '#3B82F6' },
          { label: 'Abnormal Values',      value: summary.abnormal_count, color: '#F59E0B' },
          { label: 'Risk Conditions',      value: summary.risk_count,     color: '#EF4444' },
        ].map(s => (
          <div key={s.label} className="rounded-2xl bg-slate-800/50 border border-slate-700/50 p-5 text-center">
            <p className="text-3xl font-bold" style={{ color: s.color }}>{s.value}</p>
            <p className="text-xs text-slate-500 mt-1">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-800/50 border border-slate-700/50 rounded-2xl p-1 mb-6">
        {TABS.map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 py-2.5 rounded-xl text-sm font-medium transition-all ${
              tab === t
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Tab panels */}

      {/* OVERVIEW */}
      {tab === 'Overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Radar */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6">
            <h3 className="font-semibold text-slate-200 mb-4">Parameter Overview</h3>
            {radarData.length > 0 ? (
              <ResponsiveContainer width="100%" height={260}>
                <RadarChart data={radarData} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
                  <PolarGrid stroke="rgba(148,163,184,0.2)" />
                  <PolarAngleAxis
                    dataKey="subject"
                    tick={{ fill: '#94A3B8', fontSize: 11 }}
                  />
                  <Radar
                    name="Value"
                    dataKey="value"
                    stroke="#3B82F6"
                    fill="#3B82F6"
                    fillOpacity={0.25}
                    strokeWidth={2}
                  />
                  <Tooltip
                    contentStyle={{ background: '#1E293B', border: '1px solid #334155', borderRadius: 12, fontSize: 12 }}
                    formatter={(val) => [`${val} / 150`, 'Normalised']}
                  />
                </RadarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-slate-500 text-sm text-center py-10">No parameters detected.</p>
            )}
          </div>

          {/* Abnormal summary */}
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6">
            <h3 className="font-semibold text-slate-200 mb-4">Abnormal Values</h3>
            {abnormalParams.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 gap-3">
                <CheckCircle className="w-10 h-10 text-emerald-500" />
                <p className="text-slate-400 text-sm">All detected parameters are within normal range.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {abnormalParams.map(([name, data]) => (
                  <div key={name} className="flex items-center justify-between rounded-xl bg-slate-900/50 px-4 py-3">
                    <span className="text-sm text-slate-300">{name.replace('BloodPressure', 'BP ')}</span>
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-sm text-slate-100">{data.value} {data.unit}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${
                        data.status === 'Critical' ? 'bg-red-900/50 text-red-300' :
                        data.status === 'High'     ? 'bg-red-500/20 text-red-400' :
                                                     'bg-amber-500/20 text-amber-400'
                      }`}>{data.status}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Top risks preview */}
          {risks.length > 0 && (
            <div className="lg:col-span-2 bg-slate-800/50 border border-slate-700/50 rounded-2xl p-6">
              <h3 className="font-semibold text-slate-200 mb-4">Top Risk Conditions</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {risks.slice(0, 4).map(risk => (
                  <div key={risk.id} className={`rounded-xl border p-4 ${SEVERITY_STYLE[risk.severity]}`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-sm">{risk.name}</span>
                      <span className="text-xs font-bold opacity-80">{risk.severity}</span>
                    </div>
                    <p className="text-xs opacity-80 leading-relaxed">{risk.recommendation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* PARAMETERS */}
      {tab === 'Parameters' && (
        <div>
          {paramEntries.length === 0 ? (
            <div className="text-center py-20 text-slate-500">No parameters detected in the document.</div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {paramEntries.map(([name, data]) => (
                <ResultCard key={name} name={name} data={data} />
              ))}
            </div>
          )}
        </div>
      )}

      {/* RISKS */}
      {tab === 'Risks' && (
        <div>
          {risks.length === 0 ? (
            <div className="text-center py-20">
              <CheckCircle className="w-16 h-16 text-emerald-500 mx-auto mb-4" />
              <p className="text-slate-400">No risk conditions detected.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {risks.map(risk => (
                <div key={risk.id} className={`rounded-2xl border p-6 ${SEVERITY_STYLE[risk.severity]}`}>
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="font-bold text-base">{risk.name}</h4>
                    <span className={`text-xs font-bold px-3 py-1 rounded-full border ${SEVERITY_STYLE[risk.severity]}`}>
                      {risk.severity}
                    </span>
                  </div>
                  <p className="text-sm opacity-90 leading-relaxed">
                    💡 <strong>Recommendation:</strong> {risk.recommendation}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* RAW TEXT */}
      {tab === 'Raw Text' && (
        <div className="bg-slate-900 border border-slate-700/50 rounded-2xl p-6">
          <h3 className="font-semibold text-slate-400 mb-3 text-sm uppercase tracking-widest">OCR Extracted Text</h3>
          <pre className="text-xs text-slate-400 whitespace-pre-wrap leading-relaxed font-mono overflow-auto max-h-96">
            {extracted_text || 'No raw text available.'}
          </pre>
        </div>
      )}
    </div>
  )
}
