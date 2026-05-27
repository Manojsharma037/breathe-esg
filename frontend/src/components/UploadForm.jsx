import { useState } from 'react'
import api from '../api/axios'
import './UploadForm.css'

// ─── Single Upload Section Component ───────────────
function UploadSection({ title, accept, sourceType, color }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [isError, setIsError] = useState(false)

  // File select hone pe
  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setMessage(null)
  }

  // Upload button click pe
  const handleUpload = () => {
    if (!file) {
      setMessage('Pehle file select karo!')
      setIsError(true)
      return
    }

    // FormData banao — file bhejne ke liye
    const formData = new FormData()
    formData.append('file', file)

    setLoading(true)
    setMessage(null)

    api.post(`/upload/${sourceType}/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
      .then(res => {
        setMessage(`✅ ${res.data.rows_saved} rows uploaded!`)
        setIsError(false)
        setFile(null)
        // File input reset karo
        document.getElementById(`file-${sourceType}`).value = ''
      })
      .catch(err => {
        setMessage(`❌ Upload failed: ${err.response?.data?.error || 'Unknown error'}`)
        setIsError(true)
      })
      .finally(() => {
        setLoading(false)
      })
  }

  return (
    <div className="upload-section" style={{ borderTop: `4px solid ${color}` }}>
      <h3>{title}</h3>
      <p className="accept-hint">
        {accept === '.csv' ? '📄 CSV file only' : '📋 JSON file only'}
      </p>

      <div className="upload-controls">
        <input
          id={`file-${sourceType}`}
          type="file"
          accept={accept}
          onChange={handleFileChange}
          className="file-input"
        />
        <button
          className="upload-btn"
          onClick={handleUpload}
          disabled={loading}
          style={{ background: color }}
        >
          {loading ? 'Uploading...' : '⬆ Upload'}
        </button>
      </div>

      {file && (
        <p className="file-name">📎 {file.name}</p>
      )}

      {message && (
        <p className={`upload-message ${isError ? 'error' : 'success'}`}>
          {message}
        </p>
      )}
    </div>
  )
}


// ─── Main UploadForm Component ──────────────────────
function UploadForm() {
  const [normalizing, setNormalizing] = useState(false)
  const [normalizeResult, setNormalizeResult] = useState(null)
  const [normalizeError, setNormalizeError] = useState(null)

  // Normalize button click
  const handleNormalize = () => {
    setNormalizing(true)
    setNormalizeResult(null)
    setNormalizeError(null)

    api.post('/normalize/')
      .then(res => {
        setNormalizeResult(res.data)
      })
      .catch(err => {
        setNormalizeError('Normalization failed!')
        console.error(err)
      })
      .finally(() => {
        setNormalizing(false)
      })
  }

  return (
    <div className="upload-form-container">
      <h2>📤 Data Ingestion</h2>
      <p className="subtitle">
        Upload karo → Normalize karo → Review karo
      </p>

      {/* 3 Upload Sections */}
      <div className="upload-grid">
        <UploadSection
          title="SAP — Fuel & Procurement"
          accept=".csv"
          sourceType="sap"
          color="#1565c0"
        />
        <UploadSection
          title="Utility — Electricity"
          accept=".csv"
          sourceType="utility"
          color="#6a1b9a"
        />
        <UploadSection
          title="Travel — Flights & Hotels"
          accept=".json"
          sourceType="travel"
          color="#2d6a4f"
        />
      </div>

      {/* Normalize Button */}
      <div className="normalize-section">
        <h3>⚡ Step 2 — Normalize Data</h3>
        <p>Upload and then normalize — CO2 calculate hoga</p>

        <button
          className="normalize-btn"
          onClick={handleNormalize}
          disabled={normalizing}
        >
          {normalizing ? '⏳ Normalizing...' : '⚡ Run Normalization'}
        </button>

        {/* Normalize Result */}
        {normalizeResult && (
          <div className="normalize-result success">
            <p>✅ Normalization Complete!</p>
            <p>Processed: <strong>{normalizeResult.processed}</strong></p>
            <p>Failed: <strong>{normalizeResult.failed}</strong></p>
            <p>Suspicious: <strong>{normalizeResult.suspicious}</strong></p>
          </div>
        )}

        {normalizeError && (
          <p className="normalize-result error">{normalizeError}</p>
        )}
      </div>
    </div>
  )
}

export default UploadForm