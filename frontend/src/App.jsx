import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Ingest from './pages/Ingest'
import NoveltyCheck from './pages/NoveltyCheck'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <h1 className="logo">🔬 Novelty Score Engine</h1>
            <div className="nav-links">
              <Link to="/ingest" className="nav-link">Ingest Proposal</Link>
              <Link to="/novelty-check" className="nav-link">Check Novelty</Link>
            </div>
          </div>
        </nav>
        
        <main className="main-content">
          <Routes>
            <Route path="/" element={<NoveltyCheck />} />
            <Route path="/ingest" element={<Ingest />} />
            <Route path="/novelty-check" element={<NoveltyCheck />} />
          </Routes>
        </main>
        
        <footer className="footer">
          <p>Novelty Score Engine - R&D Proposal Analysis System</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
