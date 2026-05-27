import Dashboard from './pages/Dashboard'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>🌱 BreatheESG — Emissions Dashboard</h1>
      </header>
      <main>
        <Dashboard />
      </main>
    </div>
  )
}

export default App