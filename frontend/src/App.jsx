/**
 * App.jsx — Root application component
 */
import React, { useState } from 'react'
import UploadForm from './components/UploadForm'
import Dashboard from './components/Dashboard'
import { Activity, Shield, Zap, ChevronRight } from 'lucide-react'

function Header() {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-bold text-white text-lg">MedScan</span>
            <span className="font-bold text-blue-400 text-lg"> AI</span>
          </div>
        </div>
        <div className="flex items-center gap-6 text-sm text-slate-500">
          <span className="hidden sm:flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5" /> Secure
          </span>
          <span className="hidden sm:flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5" /> Fast Analysis
          </span>
          <span className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-semibold border border-emerald-500/20">
            v1.0.0
          </span>
        </div>
      </div>
    </header>
  )
}

function HeroSection() {
  return (
    <div className="text-center mb-10 animate-fade-in w-full max-w-3xl mx-auto px-4">
      {/* Badge */}
      <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/25 rounded-full px-5 py-2 text-blue-400 text-sm font-medium mb-7">
        <Zap className="w-3.5 h-3.5" />
        AI-Powered Medical Report Analysis
      </div>

      {/* Title */}
      <h1 className="text-5xl sm:text-6xl font-extrabold mb-6 leading-tight">
        <span className="text-white">Understand Your</span>
        <br />
        <span
          style={{
            background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #06B6D4 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          Health Report
        </span>
      </h1>

      <p className="text-slate-400 text-lg max-w-xl mx-auto mb-8 leading-relaxed">
        Upload any medical report — PDF or image — and instantly get AI-powered insights,
        risk detection, and actionable recommendations.
      </p>

      {/* Feature pills */}
      <div className="flex flex-wrap justify-center gap-3 text-xs font-medium">
        {['OCR Text Extraction', '9 Biomarkers', 'Risk Detection', 'PDF Export', 'Instant Results'].map(f => (
          <span key={f} className="flex items-center gap-1.5 bg-slate-800/80 border border-slate-700/60 text-slate-400 px-4 py-2 rounded-full">
            <ChevronRight className="w-3 h-3 text-blue-500" />
            {f}
          </span>
        ))}
      </div>
    </div>
  )
}

function Footer() {
  return (
    <footer className="border-t border-slate-800 mt-10 py-8">
      <div className="w-full px-6 text-center text-sm">
        <p className="text-slate-500">
          MedScan AI · Intelligent Medical Report Analyzer ·{' '}
          <span className="text-slate-400">For demonstration purposes only.</span>
        </p>
        <p className="mt-2 text-xs text-slate-600">
          Not a substitute for professional medical advice. Always consult a qualified physician.
        </p>
      </div>
    </footer>
  )
}

export default function App() {
  const [result, setResult] = useState(null)

  return (
    <div className="min-h-screen flex flex-col" style={{ background: 'var(--brand-bg)' }}>
      <Header />

      {/* Ambient glow */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(59,130,246,0.12) 0%, transparent 70%)',
        }}
      />

      {/* ✅ FIXED: removed max-w-7xl so inner max-w-2xl/max-w-6xl can center correctly */}
      <main className="flex-1 w-full px-6 pt-14 pb-0 relative z-10 flex flex-col items-center">
        {!result ? (
          <>
            <HeroSection />
            <UploadForm onResult={setResult} />
          </>
        ) : (
          <Dashboard result={result} onReset={() => setResult(null)} />
        )}
      </main>

      <Footer />
    </div>
  )
}