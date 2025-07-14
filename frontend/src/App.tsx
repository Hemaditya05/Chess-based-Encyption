// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import EncryptApp from './EncryptApp';
import DecryptApp from './DecryptApp';
import './App.css';

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-title">
        <span role="img" aria-label="chess">♛</span> <span className="brand">Chess-Based Encryption</span>
      </div>
      <div className="navbar-links">
        <Link to="/" className="nav-link">Home</Link>
        <Link to="/encrypt" className="nav-link">Encrypt</Link>
        <Link to="/decrypt" className="nav-link">Decrypt</Link>
      </div>
    </nav>
  );
}

function LandingPage() {
  const navigate = useNavigate();
  return (
    <div className="landing-page">
      <h1 className="landing-title">Welcome to <span className="brand">Chess-Based Encryption</span></h1>
      <p className="landing-subtitle">for Secure Data Transmission and encryption for the modern era.</p>
      <div className="landing-actions">
        <button className="button primary" onClick={() => navigate('/encrypt')}>Encrypt a Message</button>
        <button className="button secondary" onClick={() => navigate('/decrypt')}>Decrypt a Message</button>
      </div>
      <div className="landing-info">
        <h2>Why ChessPerm?</h2>
        <ul>
          <li>🔒 Post-quantum security (Kyber512 KEM)</li>
          <li>♟️ Unique chess-move-based key derivation</li>
          <li>🖼️ Steganography: hide messages in images</li>
          <li>💡 Open source, privacy-first</li>
        </ul>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="app-bg">
        <Navbar />
        <div className="main-content">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/encrypt" element={<EncryptApp />} />
            <Route path="/decrypt" element={<DecryptApp />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
