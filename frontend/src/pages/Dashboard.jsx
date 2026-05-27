import { useState, useEffect } from 'react'
import RecordsTable from '../components/RecordsTable'
import UploadForm from '../components/UploadForm'
import api from '../api/axios'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Backend se stats lo
    api.get('/dashboard/stats/')
      .then(res => {
        setStats(res.data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error:', err)
        setLoading(false)
      })
  }, [])

  if (loading) return <p>Loading...</p>
  if (!stats) return <p>Stats nahi mili!</p>

  return (
    <div>
      <h2>Dashboard</h2>

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="card">
          <h3>Total Records</h3>
          <p>{stats.total_records}</p>
        </div>
        <div className="card pending">
          <h3>Pending</h3>
          <p>{stats.pending}</p>
        </div>
        <div className="card approved">
          <h3>Approved</h3>
          <p>{stats.approved}</p>
        </div>
        <div className="card rejected">
          <h3>Rejected</h3>
          <p>{stats.rejected}</p>
        </div>
        <div className="card suspicious">
          <h3>Suspicious</h3>
          <p>{stats.suspicious}</p>
        </div>
      </div>

      {/* CO2 by Scope */}
      <div className="co2-section">
        <h2>CO2 Emissions</h2>
        <div className="stats-grid">
          <div className="card scope1">
            <h3>Scope 1 (Fuel)</h3>
            <p>{stats.co2_by_scope.scope1} kgCO2e</p>
          </div>
          <div className="card scope2">
            <h3>Scope 2 (Electricity)</h3>
            <p>{stats.co2_by_scope.scope2} kgCO2e</p>
          </div>
          <div className="card scope3">
            <h3>Scope 3 (Travel)</h3>
            <p>{stats.co2_by_scope.scope3} kgCO2e</p>
          </div>
          <div className="card total">
            <h3>Total CO2</h3>
            <p>{stats.co2_by_scope.total} kgCO2e</p>
          </div>
        </div>
      </div>
      <UploadForm />
      <RecordsTable />

    </div>
  )
}

export default Dashboard
