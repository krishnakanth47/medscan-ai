/**
 * UploadForm.jsx — Drag-and-drop file upload with validation, progress, and backend status
 */
import React, { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, AlertCircle, Loader2, Wifi, WifiOff, RefreshCw } from 'lucide-react'
import axios from 'axios'

const API = import.meta.env.VITE_API_URL
const MAX_SIZE = 10 * 1024 * 1024  // 10 MB
const ACCEPTED = { 'application/pdf': ['.pdf'], 'image/jpeg': ['.jpg', '.jpeg'], 'image/png': ['.png'] }

export default function UploadForm({ onResult }) {
  const [file, setFile]             = useState(null)
  const [gender, setGender]         = useState('general')
  const [status, setStatus]         = useState(null)
  const [error, setError]           = useState(null)
  const [progress, setProgress]     = useState(0)
  const [backendOnline, setBackendOnline] = useState(null)  // null=checking, true, false

  // ── Live backend health polling ────────────────────────────────────────
  useEffect(() => {
    const check = async () => {
      try {
        await axios.get(`${API}/health`, { timeout: 4000 })
        setBackendOnline(true)
      } catch {
        setBackendOnline(false)
      }
    }
    check()
    const id = setInterval(check, 8000)
    return () => clearInterval(id)
  }, [])

  // ── Dropzone ────────────────────────────────────────────────────────────
  const onDrop = useCallback((accepted, rejected) => {
    setError(null)
    if (rejected.length) {
      const code = rejected[0].errors[0]?.code
      setError(
        code === 'file-too-large'
          ? 'File exceeds 10 MB limit.'
          : 'Invalid file type. Accepted: PDF, JPG, PNG.'
      )
      return
    }
    setFile(accepted[0])
    setStatus(null)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    maxSize: MAX_SIZE,
    multiple: false,
  })

  // ── Analyse handler ─────────────────────────────────────────────────────
  const handleAnalyze = async () => {
    if (!file) return
    setError(null)
    setProgress(0)

    try {
      // 1. Upload
      setStatus('uploading')
      const formData = new FormData()
      formData.append('file', file)
      const uploadRes = await axios.post(`${API}/upload`, formData, {
        onUploadProgress: (e) => setProgress(Math.round((e.loaded / e.total) * 50)),
        timeout: 30000,
      })
      const { report_id } = uploadRes.data
      setProgress(55)

      // 2. Analyse
      setStatus('analyzing')
      const analyzeRes = await axios.post(
        `${API}/analyze/${report_id}?gender=${gender}`,
        {},
        { timeout: 90000 }
      )
      setProgress(100)
      setStatus('done')
      setBackendOnline(true)
      onResult({ ...analyzeRes.data, report_id })

    } catch (err) {
      setStatus('error')
      setBackendOnline(false)

      // Network error (backend offline) vs server error
      if (!err.response) {
        setError(
          '⚡ Cannot connect to the backend server. ' +
          'Please run start.bat to launch both servers, then try again.'
        )
      } else {
        const detail = err.response?.data?.detail
        setError(detail || `Server error ${err.response.status}: Please try again.`)
      }
    }
  }

  // ── Status-indicator colour logic ───────────────────────────────────────
  const StatusDot = () => {
    if (backendOnline === null) return (
      <span className="flex items-center gap-1.5 text-xs text-slate-500">
        <Loader2 className="w-3 h-3 animate-spin" /> Connecting…
      </span>
    )
    if (backendOnline) return (
      <span className="flex items-center gap-1.5 text-xs text-emerald-400">
        <Wifi className="w-3 h-3" /> Backend Online
      </span>
    )
    return (
      <span className="flex items-center gap-1.5 text-xs text-red-400">
        <WifiOff className="w-3 h-3" /> Backend Offline — run start.bat
      </span>
    )
  }

  return (
    <div className="w-full max-w-2xl mx-auto animate-fade-in flex flex-col gap-6">

      {/* Backend status bar */}
      <div className="flex justify-end">
        <StatusDot />
      </div>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-3xl p-20 text-center cursor-pointer min-h-64
          transition-all duration-300
          ${isDragActive
            ? 'border-blue-400 bg-blue-500/10 scale-[1.02]'
            : file
              ? 'border-emerald-500/60 bg-emerald-500/5'
              : 'border-slate-600 bg-slate-800/40 hover:border-blue-500/60 hover:bg-blue-500/5'
          }
        `}
      >
        <input {...getInputProps()} />

        {file ? (
          <div className="flex flex-col items-center gap-4">
            <div className="w-20 h-20 rounded-2xl bg-emerald-500/20 flex items-center justify-center">
              <FileText className="w-10 h-10 text-emerald-400" />
            </div>
            <div>
              <p className="font-semibold text-slate-200 text-lg">{file.name}</p>
              <p className="text-sm text-slate-500 mt-2">{(file.size / 1024).toFixed(1)} KB — click to change</p>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-6">
            <div
              className="w-24 h-24 rounded-2xl bg-blue-500/10 flex items-center justify-center animate-pulse-ring"
              style={{ border: '2px solid rgba(59,130,246,0.4)' }}
            >
              <Upload className="w-11 h-11 text-blue-400" />
            </div>
            <div>
              <p className="text-xl font-semibold text-slate-200">
                {isDragActive ? 'Drop your report here' : 'Upload Medical Report'}
              </p>
              <p className="text-sm text-slate-500 mt-3">
                Drag &amp; drop or click — PDF, JPG, PNG up to 10 MB
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Gender selector */}
      <div className="flex items-center justify-center gap-4">
        <label className="text-sm text-slate-400 font-medium">Patient Gender:</label>
        <div className="flex gap-2">
          {['general', 'male', 'female'].map(g => (
            <button
              key={g}
              onClick={() => setGender(g)}
              className={`px-5 py-2 rounded-full text-sm font-medium transition-all
                ${gender === g
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                  : 'bg-slate-700/60 text-slate-400 hover:bg-slate-700'
                }`}
            >
              {g.charAt(0).toUpperCase() + g.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Progress bar */}
      {(status === 'uploading' || status === 'analyzing') && (
        <div>
          <div className="flex items-center justify-between text-sm mb-3">
            <span className="text-blue-400 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              {status === 'uploading' ? 'Uploading report…' : 'Analysing with OCR + AI…'}
            </span>
            <span className="text-slate-400">{progress}%</span>
          </div>
          <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-500 rounded-full transition-all duration-500"
              style={{ width: `${progress}%`, boxShadow: '0 0 12px rgba(59,130,246,0.6)' }}
            />
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 bg-red-500/10 border border-red-500/30 rounded-xl p-4">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-red-300">{error}</p>
            {!backendOnline && (
              <p className="text-xs text-slate-500 mt-2">
                💡 Tip: Double-click <strong>start.bat</strong> in the project root to launch both servers automatically.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Submit */}
      <button
        onClick={handleAnalyze}
        disabled={!file || status === 'uploading' || status === 'analyzing' || backendOnline === false}
        className={`
          w-full py-5 rounded-2xl font-semibold text-base transition-all duration-300
          ${(!file || status === 'uploading' || status === 'analyzing' || backendOnline === false)
            ? 'bg-slate-700/60 text-slate-500 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-500 text-white shadow-xl shadow-blue-500/30 hover:shadow-blue-500/50 hover:-translate-y-0.5 active:translate-y-0'
          }
        `}
      >
        {status === 'uploading' ? 'Uploading…'
          : status === 'analyzing' ? 'Analysing…'
          : backendOnline === false ? '⚠️  Backend Offline'
          : backendOnline === null ? 'Connecting…'
          : '🔬  Analyze Report'}
      </button>

    </div>
  )
}
