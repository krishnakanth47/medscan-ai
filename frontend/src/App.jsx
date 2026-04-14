```jsx
/**
 * App.jsx — Root application component
 */

import React, { useState } from 'react'
import UploadForm from './components/UploadForm'
import Dashboard from './components/Dashboard'
import { Shield, Zap, ChevronRight } from 'lucide-react'

function Header() {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">

        <div className="flex items-center gap-2">

          {/* MedScan AI Inline SVG Logo */}
          <svg
            width="38"
            height="38"
            viewBox="0 0 38 38"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            style={{ filter: 'drop-shadow(0 0 6px rgba(59,130,246,0.5))' }}
          >
            {/* Brain outline */}
            <path
              d="M19 5C13 5 8 9.5 8 15.5C8 18.5 9.2 21.2 11.2 23.2L11 30H27L26.8 23.2C28.8 21.2 30 18.5 30 15.5C30 9.5 25 5 19 5Z"
              fill="url(#brainGrad)"
              opacity="0.9"
            />

            {/* Circuit nodes */}
            <circle cx="26" cy="13" r="1.5" fill="#38BDF8" />
            <circle cx="28" cy="17" r="1" fill="#38BDF8" opacity="0.7" />
            <circle cx="25" cy="20" r="1" fill="#38BDF8" opacity="0.6" />

            <line x1="26" y1="13" x2="28" y2="17" stroke="#38BDF8" strokeWidth="0.8" opacity="0.7" />
            <line x1="28" y1="17" x2="25" y2="20" stroke="#38BDF8" strokeWidth="0.8" opacity="0.6" />

            {/* Medical cross */}
            <rect x="15" y="10" width="8" height="8" rx="1.5" fill="#1E40AF" opacity="0.85" />
            <rect x="18" y="11.5" width="2" height="5" rx="0.5" fill="white" />
            <rect x="16.5" y="13" width="5" height="2" rx="0.5" fill="white" />

            {/* Stethoscope arc */}
            <path
              d="M11 16 Q9 20 11 24"
              stroke="#1D4ED8"
              strokeWidth="1.8"
              fill="none"
              strokeLinecap="round"
            />

            <circle cx="11" cy="24.5" r="1.5" fill="#3B82F6" />

            {/* Magnifier */}
            <circle
              cx="21"
              cy="22"
              r="4"
              stroke="#1E3A8A"
              strokeWidth="1.5"
              fill="#DBEAFE"
              opacity="0.35"
            />

            <line
              x1="24"
              y1="25"
              x2="27"
              y2="28"
              stroke="#1E3A8A"
              strokeWidth="1.8"
              strokeLinecap="round"
            />

            {/* Bottom platform */}
            <rect
              x="11"
              y="29.5"
              width="16"
              height="3"
              rx="1.5"
              fill="url(#baseGrad)"
            />

            <defs>
              <linearGradient
                id="brainGrad"
                x1="8"
                y1="5"
                x2="30"
                y2="30"
                gradientUnits="userSpaceOnUse"
              >
                <stop offset="0%" stopColor="#1D4ED8" />
                <stop offset="100%" stopColor="#0EA5E9" />
              </linearGradient>

              <linearGradient
                id="baseGrad"
                x1="11"
                y1="29"
                x2="27"
                y2="32"
                gradientUnits="userSpaceOnUse"
              >
                <stop offset="0%" stopColor="#1D4ED8" />
                <stop offset="100%" stopColor="#0891B2" />
              </linearGradient>
            </defs>

          </svg>

          <div>
            <span className="font-bold text-white text-lg tracking-tight">
              MedScan
            </span>
            <span className="font-bold text-blue-400 text-lg">
              {' '}AI
            </span>
          </div>

        </div>

        <div className="flex items-center gap-6 text-sm text-slate-500">

          <span className="hidden sm:flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5" />
            Secure
          </span>

          <span className="hidden sm:flex items-center gap-1.5">
            <Zap className="w-3.5 h-3.5" />
            Fast Analysis
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
        <span className="text-white">
          Understand Your
        </span>

        <br />

        <span
          style={{
            background:
              'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 50%, #06B6D4 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
          }}
        >
          Health Report
        </span>
      </h1>

      {/* FIXED ALIGNMENT WRAPPER */}
      <div className="max-w-xl mx-auto">

        <p className="text-slate-400 text-lg mb-8 leading-relaxed">
          Upload any medical report — PDF or image — and instantly get
          AI-powered insights, risk detection, and actionable recommendations.
        </p>

        <div className="flex flex-wrap justify-center gap-3 text-xs font-medium">

          {[
            'OCR Text Extraction',
            '9 Biomarkers',
            'Risk Detection',
            'PDF Export',
            'Instant Results'
          ].map(f => (
            <span
              key={f}
              className="flex items-center gap-1.5 bg-slate-800/80 border border-slate-700/60 text-slate-400 px-4 py-2 rounded-full"
            >
              <ChevronRight className="w-3 h-3 text-blue-500" />
              {f}
            </span>
          ))}

        </div>

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
          <span className="text-slate-400">
            For demonstration purposes only.
          </span>
        </p>

        <p className="mt-2 text-xs text-slate-600">
          Not a substitute for professional medical advice.
          Always consult a qualified physician.
        </p>

      </div>
    </footer>
  )
}

export default function App() {
  const [result, setResult] = useState(null)

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ background: 'var(--brand-bg)' }}
    >

      <Header />

      {/* Ambient glow */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 80% 50% at 50% -10%, rgba(59,130,246,0.12) 0%, transparent 70%)',
        }}
      />

      <main className="flex-1 w-full px-6 pt-14 pb-0 relative z-10 flex flex-col items-center">

        {!result ? (
          <>
            <HeroSection />
            <UploadForm onResult={setResult} />
          </>
        ) : (
          <Dashboard
            result={result}
            onReset={() => setResult(null)}
          />
        )}

      </main>

      <Footer />

    </div>
  )
}
```
