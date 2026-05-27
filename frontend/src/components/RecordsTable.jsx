import { useState, useEffect } from 'react'
import api from '../api/axios'
import './RecordsTable.css'

function RecordsTable() {
  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  const fetchRecords = (status = 'all') => {
    setLoading(true)
    let url = '/records/'
    if (status !== 'all') {
      url = `/records/?review_status=${status}`
    }
    api.get(url)
      .then(res => {
        setRecords(res.data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Records fetch error:', err)
        setLoading(false)
      })
  }

  useEffect(() => {
    fetchRecords()
  }, [])

  const handleFilter = (status) => {
    setFilter(status)
    fetchRecords(status)
  }

  const handleApprove = (id) => {
    api.post(`/records/${id}/approve/`)
      .then(() => {
        alert(`Record #${id} approved!`)
        fetchRecords(filter)
      })
      .catch(err => {
        alert('Approve nahi hua!')
        console.error(err)
      })
  }

  const handleReject = (id) => {
    api.post(`/records/${id}/reject/`)
      .then(() => {
        alert(`Record #${id} rejected!`)
        fetchRecords(filter)
      })
      .catch(err => {
        alert('Reject nahi hua!')
        console.error(err)
      })
  }

  const getStatusBadge = (status) => {
    const colors = {
      'pending':    'badge-pending',
      'approved':   'badge-approved',
      'rejected':   'badge-rejected',
      'suspicious': 'badge-suspicious',
    }
    return (
      <span className={`badge ${colors[status] || ''}`}>
        {status}
      </span>
    )
  }

  const formatScope = (scope) => {
    const map = {
      'scope1': 'Scope 1',
      'scope2': 'Scope 2',
      'scope3': 'Scope 3',
    }
    return map[scope] || scope
  }

  return (
    <div className="records-container">
      <h2>Emission Records</h2>

      {/* Filter Buttons */}
      <div className="filter-buttons">
        {['all', 'pending', 'approved', 'rejected', 'suspicious'].map(f => (
          <button
            key={f}
            className={`filter-btn ${filter === f ? 'active' : ''} ${f === 'suspicious' && filter === 'suspicious' ? 'suspicious-active' : ''}`}
            onClick={() => handleFilter(f)}
          >
            {f === 'suspicious' ? '⚠️ ' : ''}
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {loading && <p className="loading">Loading...</p>}

      {!loading && records.length === 0 && (
        <p className="no-records">No suspicious Records!</p>
      )}

      {!loading && records.length > 0 && (
        <div className="table-wrapper">
          <table className="records-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Category</th>
                <th>Scope</th>
                <th>Source</th>
                <th>CO2 (kgCO2e)</th>
                <th>Period</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {records.map(record => (
                <tr
                  key={record.id}
                  className={record.is_suspicious ? 'suspicious-row' : ''}
                >
                  <td>#{record.id}</td>

                  {/* Category + Suspicious Icon */}
                  <td>
                    {record.category}
                    {record.is_suspicious && (
                      <span
                        className="suspicious-icon"
                        title={record.suspicious_reason || 'Suspicious value detected!'}
                      >
                        ⚠️
                      </span>
                    )}
                  </td>

                  <td>{formatScope(record.scope)}</td>

                  <td>
                    <span className={`source-badge source-${record.source_type}`}>
                      {record.source_type?.toUpperCase()}
                    </span>
                  </td>

                  <td className="co2-value">
                    {parseFloat(record.co2_equivalent).toFixed(2)}
                  </td>

                  <td className="period">
                    {record.period_start} → {record.period_end}
                  </td>

                  {/* Status + Suspicious Badge */}
                  <td>
                    {getStatusBadge(record.review_status)}
                    {record.is_suspicious && (
                      <span
                        className="suspicious-tooltip"
                        title={record.suspicious_reason || 'Value is 3x higher than average!'}
                      >
                        🚨
                      </span>
                    )}
                  </td>

                  <td>
                    {record.review_status === 'pending' && (
                      <div className="action-buttons">
                        <button
                          className="btn-approve"
                          onClick={() => handleApprove(record.id)}
                        >
                          ✓ Approve
                        </button>
                        <button
                          className="btn-reject"
                          onClick={() => handleReject(record.id)}
                        >
                          ✗ Reject
                        </button>
                      </div>
                    )}
                    {record.review_status !== 'pending' && (
                      <span className="reviewed">Reviewed</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default RecordsTable